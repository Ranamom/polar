import uuid
from collections.abc import Sequence
from enum import StrEnum
from typing import Any, cast

from sqlalchemy import Select, UnaryExpression, asc, desc, func, or_, select
from sqlalchemy.orm import aliased, joinedload, subqueryload

from polar.authz.service import AccessType, Authz
from polar.exceptions import NotPermitted, ResourceNotFound
from polar.kit.pagination import PaginationParams, paginate
from polar.kit.sorting import Sorting
from polar.models import (
    Account,
    Issue,
    Pledge,
    Subscription,
    Transaction,
    User,
)
from polar.models.transaction import TransactionType
from polar.models.user_organization import UserOrganization
from polar.postgres import AsyncSession

from ..schemas import (
    TransactionsBalance,
    TransactionsSummary,
)
from .base import BaseTransactionService


class SearchSortProperty(StrEnum):
    created_at = "created_at"
    amount = "amount"


class TransactionService(BaseTransactionService):
    async def search(
        self,
        session: AsyncSession,
        user: User,
        *,
        type: TransactionType | None = None,
        account_id: uuid.UUID | None = None,
        payment_user_id: uuid.UUID | None = None,
        payment_organization_id: uuid.UUID | None = None,
        pagination: PaginationParams,
        sorting: list[Sorting[SearchSortProperty]] = [
            (SearchSortProperty.created_at, True)
        ],
    ) -> tuple[Sequence[Transaction], int]:
        statement = self._get_readable_transactions_statement(user)

        statement = statement.options(
            # Pledge
            subqueryload(Transaction.pledge).options(
                # Pledge.issue
                joinedload(Pledge.issue).options(
                    joinedload(Issue.repository),
                    joinedload(Issue.organization),
                )
            ),
            # IssueReward
            subqueryload(Transaction.issue_reward),
            # Subscription
            subqueryload(Transaction.subscription).options(
                joinedload(Subscription.subscription_tier),
            ),
        )

        if type is not None:
            statement = statement.where(Transaction.type == type)
        if account_id is not None:
            statement = statement.where(Transaction.account_id == account_id)
        if payment_user_id is not None:
            statement = statement.where(Transaction.payment_user_id == payment_user_id)
        if payment_organization_id is not None:
            statement = statement.where(
                Transaction.payment_organization_id == payment_organization_id
            )

        order_by_clauses: list[UnaryExpression[Any]] = []
        for criterion, is_desc in sorting:
            clause_function = desc if is_desc else asc
            if criterion == SearchSortProperty.created_at:
                order_by_clauses.append(clause_function(Transaction.created_at))
            elif criterion == SearchSortProperty.amount:
                order_by_clauses.append(clause_function(Transaction.amount))

        results, count = await paginate(session, statement, pagination=pagination)

        return results, count

    async def lookup(
        self, session: AsyncSession, id: uuid.UUID, user: User
    ) -> Transaction:
        statement = (
            self._get_readable_transactions_statement(user)
            .options(
                # Pledge
                subqueryload(Transaction.pledge).options(
                    # Pledge.issue
                    joinedload(Pledge.issue).options(
                        joinedload(Issue.repository),
                        joinedload(Issue.organization),
                    )
                ),
                # IssueReward
                subqueryload(Transaction.issue_reward),
                # Subscription
                subqueryload(Transaction.subscription).options(
                    joinedload(Subscription.subscription_tier),
                ),
                # Paid transactions
                subqueryload(Transaction.paid_transactions),
            )
            .where(Transaction.id == id)
        )
        result = await session.execute(statement)
        transaction = result.scalar_one_or_none()
        if transaction is None:
            raise ResourceNotFound()

        return transaction

    async def get_summary(
        self, session: AsyncSession, user: User, account: Account, authz: Authz
    ) -> TransactionsSummary:
        if not await authz.can(user, AccessType.read, account):
            raise NotPermitted()

        statement = (
            select(
                Transaction.currency,
                Transaction.account_currency,
                cast(type[int], func.coalesce(func.sum(Transaction.amount), 0)),
                cast(type[int], func.coalesce(func.sum(Transaction.account_amount), 0)),
                cast(
                    type[int],
                    func.coalesce(
                        func.sum(Transaction.amount).filter(
                            Transaction.type == TransactionType.payout
                        ),
                        0,
                    ),
                ),
                cast(
                    type[int],
                    func.coalesce(
                        func.sum(Transaction.account_amount).filter(
                            Transaction.type == TransactionType.payout
                        ),
                        0,
                    ),
                ),
            )
            .where(Transaction.account_id == account.id)
            .group_by(Transaction.currency, Transaction.account_currency)
        )

        result = await session.execute(statement)
        (
            currency,
            account_currency,
            amount,
            account_amount,
            payout_amount,
            account_payout_amount,
        ) = result.one()._tuple()

        return TransactionsSummary(
            balance=TransactionsBalance(
                currency=currency,
                amount=amount,
                account_currency=account_currency,
                account_amount=account_amount,
            ),
            payout=TransactionsBalance(
                currency=currency,
                amount=payout_amount,
                account_currency=account_currency,
                account_amount=account_payout_amount,
            ),
        )

    def _get_readable_transactions_statement(self, user: User) -> Select[Any]:
        PaymentUserOrganization = aliased(UserOrganization)
        statement = (
            select(Transaction)
            .join(Transaction.account, isouter=True)
            .join(Account.organization, isouter=True)
            .join(
                UserOrganization,
                onclause=Account.organization_id == UserOrganization.organization_id,
                isouter=True,
            )
            .join(
                PaymentUserOrganization,
                onclause=Transaction.payment_organization_id
                == PaymentUserOrganization.organization_id,
                isouter=True,
            )
            .where(
                or_(
                    Account.user_id == user.id,
                    UserOrganization.user_id == user.id,
                    Transaction.payment_user_id == user.id,
                    PaymentUserOrganization.user_id == user.id,
                )
            )
        )

        return statement


transaction = TransactionService(Transaction)