import uuid
from collections.abc import Iterable
from datetime import date, datetime
from typing import Any, Literal, Self

import stripe as stripe_lib
from pydantic import UUID4, AnyHttpUrl, EmailStr, Field, root_validator, validator

from polar.enums import Platforms
from polar.kit.schemas import Schema, TimestampedSchema
from polar.models.subscription import Subscription as SubscriptionModel
from polar.models.subscription import SubscriptionStatus
from polar.models.subscription_benefit import (
    SubscriptionBenefitArticlesProperties,
    SubscriptionBenefitCustomProperties,
    SubscriptionBenefitProperties,
    SubscriptionBenefitType,
)
from polar.models.subscription_tier import SubscriptionTier as SubscriptionTierModel
from polar.models.subscription_tier import SubscriptionTierType
from polar.models.user import User

TIER_NAME_MIN_LENGTH = 3
TIER_NAME_MAX_LENGTH = 24
TIER_DESCRIPTION_MAX_LENGTH = 240
BENEFIT_DESCRIPTION_MIN_LENGTH = 3
BENEFIT_DESCRIPTION_MAX_LENGTH = 42


# SubscriptionBenefitCreate


class SubscriptionBenefitCreateBase(Schema):
    description: str = Field(
        ...,
        min_length=BENEFIT_DESCRIPTION_MIN_LENGTH,
        max_length=BENEFIT_DESCRIPTION_MAX_LENGTH,
    )
    organization_id: UUID4 | None = None
    repository_id: UUID4 | None = None
    properties: SubscriptionBenefitProperties

    @root_validator
    def check_either_organization_or_repository(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        organization_id = values.get("organization_id")
        repository_id = values.get("repository_id")
        if organization_id is not None and repository_id is not None:
            raise ValueError(
                "Subscription benefits should either be linked to "
                "an Organization or a Repository, not both."
            )
        if organization_id is None and repository_id is None:
            raise ValueError(
                "Subscription benefits should be linked to "
                "an Organization or a Repository."
            )
        return values


class SubscriptionBenefitCustomCreate(SubscriptionBenefitCreateBase):
    type: Literal[SubscriptionBenefitType.custom]
    is_tax_applicable: bool
    properties: SubscriptionBenefitCustomProperties


# This is a dummy schema only there to produce a valid union below
# Remove it when we have other create schemas to add
class SubscriptionBenefitCustomBisCreate(SubscriptionBenefitCustomCreate):
    ...


SubscriptionBenefitCreate = (
    SubscriptionBenefitCustomCreate | SubscriptionBenefitCustomBisCreate
)


# SubscriptionBenefitUpdate


class SubscriptionBenefitUpdateBase(Schema):
    description: str | None = Field(
        None,
        min_length=BENEFIT_DESCRIPTION_MIN_LENGTH,
        max_length=BENEFIT_DESCRIPTION_MAX_LENGTH,
    )


class SubscriptionBenefitArticlesUpdate(SubscriptionBenefitUpdateBase):
    # Don't allow to update properties, as both Free and Premium posts
    # are pre-created by us and shouldn't change
    ...


class SubscriptionBenefitCustomUpdate(SubscriptionBenefitUpdateBase):
    properties: SubscriptionBenefitCustomProperties | None = None


SubscriptionBenefitUpdate = (
    SubscriptionBenefitArticlesUpdate | SubscriptionBenefitCustomUpdate
)


# SubscriptionBenefit


class SubscriptionBenefitBase(TimestampedSchema):
    id: UUID4
    type: SubscriptionBenefitType
    description: str
    selectable: bool
    deletable: bool
    organization_id: UUID4 | None = None
    repository_id: UUID4 | None = None


class SubscriptionBenefitArticles(SubscriptionBenefitBase):
    type: Literal[SubscriptionBenefitType.articles]
    properties: SubscriptionBenefitArticlesProperties


class SubscriptionBenefitCustom(SubscriptionBenefitBase):
    type: Literal[SubscriptionBenefitType.custom]
    properties: SubscriptionBenefitCustomProperties
    is_tax_applicable: bool


SubscriptionBenefit = SubscriptionBenefitArticles | SubscriptionBenefitCustom

subscription_benefit_schema_map: dict[
    SubscriptionBenefitType, type[SubscriptionBenefit]
] = {
    SubscriptionBenefitType.articles: SubscriptionBenefitArticles,
    SubscriptionBenefitType.custom: SubscriptionBenefitCustom,
}


# SubscriptionTier


class SubscriptionTierCreate(Schema):
    type: Literal[
        SubscriptionTierType.hobby,
        SubscriptionTierType.pro,
        SubscriptionTierType.business,
    ]
    name: str = Field(
        ..., min_length=TIER_NAME_MIN_LENGTH, max_length=TIER_NAME_MAX_LENGTH
    )
    description: str | None = Field(
        default=None, max_length=TIER_DESCRIPTION_MAX_LENGTH
    )
    is_highlighted: bool = False
    price_amount: int = Field(..., gt=0)
    price_currency: str = Field("USD", regex="USD")
    organization_id: UUID4 | None = None
    repository_id: UUID4 | None = None

    @root_validator
    def check_either_organization_or_repository(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        organization_id = values.get("organization_id")
        repository_id = values.get("repository_id")
        if organization_id is not None and repository_id is not None:
            raise ValueError(
                "Subscription tiers should either be linked to "
                "an Organization or a Repository, not both."
            )
        if organization_id is None and repository_id is None:
            raise ValueError(
                "Subscription tiers should be linked to "
                "an Organization or a Repository."
            )
        return values


class SubscriptionTierUpdate(Schema):
    name: str | None = Field(
        default=None, min_length=TIER_NAME_MIN_LENGTH, max_length=TIER_NAME_MAX_LENGTH
    )
    description: str | None = Field(
        default=None, max_length=TIER_DESCRIPTION_MAX_LENGTH
    )
    is_highlighted: bool | None = None
    price_amount: int | None = Field(default=None, gt=0)
    price_currency: str | None = Field(default=None, regex="USD")


class SubscriptionTierBenefitsUpdate(Schema):
    benefits: list[UUID4]


class SubscriptionTierBenefit(SubscriptionBenefitBase):
    ...


class SubscriptionTier(TimestampedSchema):
    id: UUID4
    type: SubscriptionTierType
    name: str
    description: str | None = None
    is_highlighted: bool
    price_amount: int
    price_currency: str
    is_archived: bool
    organization_id: UUID4 | None = None
    repository_id: UUID4 | None = None
    benefits: list[SubscriptionTierBenefit]

    @validator("benefits", pre=True)
    def benefits_association_proxy_fix(
        cls, v: Iterable[SubscriptionTierBenefit]
    ) -> list[SubscriptionTierBenefit]:
        # FIXME: Not needed in Pydantic V2
        return list(v)


# SubscribeSession


class SubscribeSessionCreate(Schema):
    tier_id: UUID4 = Field(
        ...,
        description="ID of the Subscription Tier to subscribe to.",
    )
    success_url: AnyHttpUrl = Field(
        ...,
        description=(
            "URL where the backer will be redirected after a successful subscription. "
            "You can add the `session_id={CHECKOUT_SESSION_ID}` query parameter "
            "to retrieve the subscribe session id."
        ),
    )
    organization_subscriber_id: UUID4 | None = Field(
        None,
        description=(
            "ID of the Organization on behalf which you want to subscribe this tier to. "
            "You need to be an administrator of the Organization to do this."
        ),
    )
    customer_email: EmailStr | None = Field(
        None,
        description=(
            "If you already know the email of your backer, you can set it. "
            "It'll be pre-filled on the subscription page."
        ),
    )


class SubscribeSession(Schema):
    id: str = Field(
        ...,
        description=("ID of the subscribe session."),
    )
    url: str | None = Field(
        None,
        description=(
            "URL where you should redirect your backer "
            "so they can subscribe to the selected tier."
        ),
    )
    customer_email: str | None = None
    customer_name: str | None = None
    organization_subscriber_id: UUID4 | None = None
    subscription_tier: SubscriptionTier
    organization_name: str | None = None
    repository_name: str | None = None

    @classmethod
    def from_db(
        cls,
        checkout_session: stripe_lib.checkout.Session,
        subscription_tier: SubscriptionTierModel,
    ) -> Self:
        organization_subscriber_id: uuid.UUID | None = None
        if checkout_session.metadata:
            try:
                organization_subscriber_id = uuid.UUID(
                    checkout_session.metadata["organization_subscriber_id"]
                )
            except (KeyError, ValueError):
                pass

        return cls(
            id=checkout_session.id,
            url=checkout_session.url,
            customer_email=checkout_session.customer_details["email"]
            if checkout_session.customer_details
            else checkout_session.customer_email,
            customer_name=checkout_session.customer_details["name"]
            if checkout_session.customer_details
            else None,
            organization_subscriber_id=organization_subscriber_id,
            subscription_tier=subscription_tier,  # type: ignore
            organization_name=subscription_tier.organization.name
            if subscription_tier.organization is not None
            else None,
            repository_name=subscription_tier.repository.name
            if subscription_tier.repository is not None
            else None,
        )


# Subscriptions


class SubscriptionUser(Schema):
    name: str
    github_username: str | None = None
    avatar_url: str | None
    email: str | None

    class Config:
        orm_mode = False

    @classmethod
    def from_db(cls, user: User, include_user_email: bool) -> Self:
        # show usernames if the user has a connected github account
        gh = user.get_platform_oauth_account(Platforms.github)
        if gh:
            return cls(
                name=user.username,
                github_username=user.username,
                avatar_url=user.avatar_url,
                email=user.email if include_user_email else None,
            )

        return cls(
            # The username is an email address. Do not show it. Use the first character as a workaround.
            name=user.username[0],
            avatar_url=user.avatar_url,
            email=user.email if include_user_email else None,
        )


class SubscriptionOrganization(Schema):
    name: str
    platform: Platforms
    avatar_url: str


class Subscription(TimestampedSchema):
    id: UUID4
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime | None = None
    cancel_at_period_end: bool
    started_at: datetime | None = None
    ended_at: datetime | None = None

    price_currency: str
    price_amount: int

    user_id: UUID4
    organization_id: UUID4 | None = None
    subscription_tier_id: UUID4

    user: SubscriptionUser
    organization: SubscriptionOrganization | None = None
    subscription_tier: SubscriptionTier

    class Config:
        orm_mode = False

    @classmethod
    def from_db(cls, subscription: SubscriptionModel, include_user_email: bool) -> Self:
        return cls(
            id=subscription.id,
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            started_at=subscription.started_at,
            ended_at=subscription.ended_at,
            price_currency=subscription.price_currency,
            price_amount=subscription.price_amount,
            user_id=subscription.user_id,
            organization_id=subscription.organization_id,
            subscription_tier_id=subscription.subscription_tier_id,
            user=SubscriptionUser.from_db(
                subscription.user, include_user_email=include_user_email
            ),
            organization=SubscriptionOrganization.from_orm(subscription.organization)
            if subscription.organization
            else None,
            subscription_tier=SubscriptionTier.from_orm(subscription.subscription_tier),
            created_at=subscription.created_at,
            modified_at=subscription.modified_at,
        )


class FreeSubscriptionCreate(Schema):
    tier_id: UUID4 = Field(
        ...,
        description="ID of the free Subscription Tier to subscribe to.",
    )
    customer_email: EmailStr | None = Field(
        None,
        description=(
            "Email of your backer. "
            "This field is required if the API is called outside the Polar app."
        ),
    )


class SubscriptionUpgrade(Schema):
    subscription_tier_id: UUID4


class SubscriptionSummary(Schema):
    user: SubscriptionUser
    organization: SubscriptionOrganization | None = None
    subscription_tier: SubscriptionTier

    class Config:
        orm_mode = False

    @classmethod
    def from_db(cls, subscription: SubscriptionModel, include_user_email: bool) -> Self:
        return cls(
            user=SubscriptionUser.from_db(
                subscription.user, include_user_email=include_user_email
            ),
            organization=SubscriptionOrganization.from_orm(subscription.organization)
            if subscription.organization
            else None,
            subscription_tier=SubscriptionTier.from_orm(subscription.subscription_tier),
        )


class SubscriptionsStatisticsPeriod(Schema):
    start_date: date
    end_date: date
    subscribers: int
    mrr: int
    cumulative: int


class SubscriptionsStatistics(Schema):
    periods: list[SubscriptionsStatisticsPeriod]


class SubscriptionsImported(Schema):
    count: int
