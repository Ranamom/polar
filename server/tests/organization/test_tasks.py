import uuid

import pytest
from pytest_mock import MockerFixture

from polar.models import Organization, SubscriptionBenefit
from polar.models.subscription_benefit import SubscriptionBenefitType
from polar.organization.tasks import (  # type: ignore[attr-defined]
    OrganizationDoesNotExist,
    organization_post_install,
    subscription_benefit_service,
    subscription_tier_service,
)
from polar.subscription.service.subscription_benefit import SubscriptionBenefitService
from polar.subscription.service.subscription_tier import SubscriptionTierService
from polar.worker import JobContext, PolarWorkerContext


@pytest.mark.asyncio
class TestOrganizationPostInstall:
    async def test_not_existing_organization(
        self, job_context: JobContext, polar_worker_context: PolarWorkerContext
    ) -> None:
        with pytest.raises(OrganizationDoesNotExist):
            await organization_post_install(
                job_context, uuid.uuid4(), polar_worker_context
            )

    async def test_existing_organization(
        self,
        mocker: MockerFixture,
        job_context: JobContext,
        polar_worker_context: PolarWorkerContext,
        organization: Organization,
    ) -> None:
        subscription_benefit = SubscriptionBenefit(
            type=SubscriptionBenefitType.articles,
            description="Public posts",
            is_tax_applicable=SubscriptionBenefitType.articles.is_tax_applicable(),
            properties={"paid_articles": False},
            organization=organization,
        )
        get_or_create_articles_benefits_mock = mocker.patch.object(
            subscription_benefit_service,
            "get_or_create_articles_benefits",
            spec=SubscriptionBenefitService.get_or_create_articles_benefits,
        )
        get_or_create_articles_benefits_mock.return_value = (
            subscription_benefit,
            subscription_benefit,
        )
        create_free_mock = mocker.patch.object(
            subscription_tier_service,
            "create_free",
            spec=SubscriptionTierService.create_free,
        )

        await organization_post_install(
            job_context, organization.id, polar_worker_context
        )

        get_or_create_articles_benefits_mock.assert_called_once()
        create_free_mock.assert_called_once()
