'use client'

import { StaggerReveal } from '@/components/Shared/StaggerReveal'
import Link from 'next/link'
import { LogoIcon } from 'polarkit/components/brand'
import { Avatar, Button } from 'polarkit/components/ui/atoms'
import { useMemo } from 'react'
import BrowserRender from './Posts/BrowserRender'
import { RenderArticle } from './Posts/markdown'

const defaultStaggerTransition = {
  staggerChildren: 0.2,
}

const defaultRevealTransition = {
  duration: 1,
}

interface LongformPostProps {
  article: RenderArticle
  staggerTransition?: typeof defaultStaggerTransition
  revealTransition?: typeof defaultRevealTransition
  showPaywalledContent?: boolean
}

export default function LongformPost({
  article,
  staggerTransition,
  revealTransition,
  showPaywalledContent,
}: LongformPostProps) {
  const organization = article.organization

  staggerTransition = staggerTransition ?? defaultStaggerTransition
  revealTransition = revealTransition ?? defaultRevealTransition

  const publishedDate = useMemo(
    () => (article.published_at ? new Date(article.published_at) : undefined),
    [article],
  )
  const publishedDateText = useMemo(
    () =>
      publishedDate
        ? new Date() > publishedDate
          ? publishedDate.toLocaleString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })
          : `Scheduled on ${publishedDate.toLocaleString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}`
        : 'Unpublished',
    [publishedDate],
  )

  return (
    <StaggerReveal className="max-w-2xl" transition={staggerTransition}>
      <div className="flex flex-col items-center gap-y-16 pb-16 pt-4">
        <StaggerReveal.Child transition={revealTransition}>
          <LogoIcon className="text-blue-500 dark:text-blue-400" size={40} />
        </StaggerReveal.Child>
        <StaggerReveal.Child transition={revealTransition}>
          <span className="dark:text-polar-500 text-gray-500">
            {publishedDateText}
          </span>
        </StaggerReveal.Child>
        <StaggerReveal.Child transition={revealTransition}>
          <h1 className="text-center text-4xl font-bold leading-normal md:leading-relaxed">
            {article.title}
          </h1>
        </StaggerReveal.Child>
        <StaggerReveal.Child transition={revealTransition}>
          <div className="flex flex-row items-center gap-x-3">
            <Avatar
              className="h-8 w-8"
              avatar_url={article.byline.avatar_url}
              name={article.byline.name}
            />
            <h3 className="text-md dark:text-polar-50">
              {article.byline.name}
            </h3>
          </div>
        </StaggerReveal.Child>
      </div>

      <StaggerReveal.Child transition={revealTransition}>
        <div className="prose dark:prose-pre:bg-polar-800 prose-pre:bg-gray-100 dark:prose-invert prose-pre:rounded-2xl dark:prose-headings:text-polar-50 prose-headings:font-normal prose-p:text-gray-600 prose-img:rounded-2xl dark:prose-p:text-polar-300 prose-a:text-blue-500 hover:prose-a:text-blue-400 dark:hover:prose-a:text-blue-300 dark:prose-a:text-blue-400 prose-a:no-underline mb-8 w-full max-w-none space-y-16">
          <BrowserRender
            article={article}
            showPaywalledContent={showPaywalledContent}
          />
        </div>
      </StaggerReveal.Child>

      <StaggerReveal.Child
        className="flex flex-col gap-y-16"
        transition={revealTransition}
      >
        <div className="dark:bg-polar-800 flex flex-col items-center gap-y-6 rounded-3xl bg-gray-100 p-8 py-12 md:px-16">
          <Avatar
            className="h-12 w-12"
            avatar_url={article.organization.avatar_url}
            name={article.organization.pretty_name || article.organization.name}
          />
          <h2 className="text-xl font-medium">
            Subscribe to{' '}
            {article.organization.pretty_name || article.organization.name}
          </h2>
          <p className="dark:text-polar-300 text-center text-gray-500">
            {organization?.bio
              ? organization?.bio
              : `Support ${
                  article.organization.pretty_name || article.organization.name
                } by subscribing to their work and get access to exclusive content.`}
          </p>
          <Link href={`/${organization.name}/subscriptions`}>
            <Button className="mt-4">Subscribe</Button>
          </Link>
        </div>
      </StaggerReveal.Child>
    </StaggerReveal>
  )
}
