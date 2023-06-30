import Gatekeeper from '@/components/Dashboard/Gatekeeper/Gatekeeper'
import Transactions from '@/components/Dashboard/Transactions/Transactions'
import DashboardLayout from '@/components/Layout/DashboardLayout'
import type { NextLayoutComponentType } from 'next'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useListPledgesForOrganization } from 'polarkit/hooks'
import { ReactElement, useEffect } from 'react'
import { useCurrentOrgAndRepoFromURL } from '../../../../hooks'

const Page: NextLayoutComponentType = () => {
  const router = useRouter()
  const { org, isLoaded } = useCurrentOrgAndRepoFromURL()

  useEffect(() => {
    if (isLoaded && !org) {
      router.push('/dashboard')
      return
    }
  }, [isLoaded, org, router])

  const pledges = useListPledgesForOrganization(org?.platform, org?.name)

  return (
    <>
      <Head>
        <title>Polar{org ? ` ${org.name}` : ''}</title>
      </Head>
      {org && pledges.data && (
        <Transactions pledges={pledges.data} org={org} tab="rewarded" />
      )}
    </>
  )
}

Page.getLayout = (page: ReactElement) => {
  return (
    <Gatekeeper>
      <DashboardLayout isPersonalDashboard={false}>{page}</DashboardLayout>
    </Gatekeeper>
  )
}

export default Page