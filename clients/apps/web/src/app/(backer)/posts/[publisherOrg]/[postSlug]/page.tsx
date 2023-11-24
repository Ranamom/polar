'use client'

import LongformPost from '@/components/Feed/LongformPost'
import { ArrowBackOutlined } from '@mui/icons-material'
import Link from 'next/link'
import { Button } from 'polarkit/components/ui/atoms'
import { useArticleLookup } from 'polarkit/hooks'

export default function Page({
  params,
}: {
  params: { publisherOrg: string; postSlug: string }
}) {
  const post = useArticleLookup(params.publisherOrg, params.postSlug)

  return (
    <div className="dark:bg-polar-800 dark:border-polar-700 relative my-16 flex flex-row items-start rounded-3xl bg-white p-12 shadow-lg dark:border">
      <Link className="absolute left-16 top-16 flex-shrink" href="/posts">
        <Button
          size="sm"
          variant="secondary"
          className="group flex h-8 w-8 flex-col items-center justify-center rounded-full border"
        >
          <ArrowBackOutlined fontSize="inherit" />
        </Button>
      </Link>
      <div className="flex w-full flex-grow flex-col items-center gap-y-8 pb-12">
        {post.data ? <LongformPost post={post.data} /> : null}
      </div>
    </div>
  )
}