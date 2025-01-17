import {
  Article,
  ArticleCreate,
  ArticleReceiversResponse,
  ArticleUpdate,
  ListResourceArticle,
  Platforms,
} from '@polar-sh/sdk'
import {
  UseMutationResult,
  UseQueryResult,
  useMutation,
  useQuery,
} from '@tanstack/react-query'
import { api, queryClient } from '../../api'
import { defaultRetry } from './retry'

export const useOrganizationArticles = (variables: {
  orgName?: string
  platform?: Platforms
  showUnpublished?: boolean
}): UseQueryResult<ListResourceArticle> =>
  useQuery({
    queryKey: [
      'article',
      'organization',
      variables.orgName,
      variables.showUnpublished,
    ],
    queryFn: () =>
      api.articles.search({
        organizationName: variables.orgName ?? '',
        platform: variables.platform ?? Platforms.GITHUB,
        showUnpublished: variables.showUnpublished,
        limit: 100,
      }),
    retry: defaultRetry,
    enabled: !!variables.orgName,
  })

export const useListArticles = (): UseQueryResult<ListResourceArticle> =>
  useQuery({
    queryKey: ['article', 'list'],
    queryFn: () => api.articles.list(),
    retry: defaultRetry,
  })

export const useCreateArticle = (): UseMutationResult<
  Article,
  Error,
  ArticleCreate,
  unknown
> =>
  useMutation({
    mutationFn: (articleCreate: ArticleCreate) =>
      api.articles.create({
        articleCreate,
      }),
    onSuccess: (result, variables, ctx) => {
      queryClient.invalidateQueries({
        queryKey: ['article', 'organization', result.organization.name],
      })
      queryClient.invalidateQueries({
        queryKey: ['article', 'list'],
      })
    },
  })

export const useUpdateArticle = () =>
  useMutation({
    mutationFn: (variables: { id: string; articleUpdate: ArticleUpdate }) =>
      api.articles.update({
        id: variables.id,
        articleUpdate: variables.articleUpdate,
      }),
    onSuccess: (result, variables, ctx) => {
      queryClient.invalidateQueries({
        queryKey: ['article', 'organization', result.organization.name],
      })
      queryClient.invalidateQueries({
        queryKey: ['article', 'id', result.id],
      })
      queryClient.invalidateQueries({
        queryKey: ['article', 'lookup'],
      })
      queryClient.invalidateQueries({
        queryKey: ['article', 'list'],
      })
    },
  })

export const useDeleteArticle = () =>
  useMutation({
    mutationFn: (variables: { id: string }) =>
      api.articles._delete({
        id: variables.id,
      }),
    onSuccess: (result, variables, ctx) => {
      queryClient.invalidateQueries({
        queryKey: ['article'],
      })
    },
  })

export const useArticle = (id: string) =>
  useQuery({
    queryKey: ['article', 'id', id],
    queryFn: () => api.articles.get({ id }),
    retry: defaultRetry,
    enabled: !!id,
  })

export const useArticleLookup = (organization_name?: string, slug?: string) =>
  useQuery({
    queryKey: ['article', 'lookup', organization_name, slug],
    queryFn: () =>
      api.articles.lookup({
        platform: Platforms.GITHUB,
        organizationName: organization_name || '',
        slug: slug || '',
      }),
    retry: defaultRetry,
    enabled: !!organization_name && !!slug,
  })

export const useArticleReceivers = (
  organizationName: string,
  paidSubscribersOnly: boolean,
): UseQueryResult<ArticleReceiversResponse> =>
  useQuery({
    queryKey: ['article', 'receivers', organizationName, paidSubscribersOnly],
    queryFn: () =>
      api.articles.receivers({
        platform: Platforms.GITHUB,
        organizationName,
        paidSubscribersOnly,
      }),
    retry: defaultRetry,
  })

export const useSendArticlePreview = () =>
  useMutation({
    mutationFn: ({ id, email }: { id: string; email: string }) =>
      api.articles.sendPreview({
        id,
        articlePreview: {
          email,
        },
      }),
  })
