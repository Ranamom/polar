import Markdown from 'markdown-to-jsx'

import { Container } from '@react-email/components'
import Embed from './EmailEmbed'
import Iframe from './EmailIframe'
import EmailMermaid from './EmailMermaid'
import Paywall from './Paywall'
import Poll from './Poll'
import EmailSyntaxHighlighter from './SyntaxHighlighter/EmailSyntaxHighlighter'
import {
  RenderArticle,
  markdownOpts,
  wrapStrictCreateElement,
} from './markdown'

export const opts = {
  ...markdownOpts,
  overrides: {
    ...markdownOpts.overrides,

    // email overrides
    poll: (args: any) => <Poll {...args} renderer={EmailPoll} />,
    paywall: (args: any) => <Paywall {...args} />,
    SubscribeNow: () => <></>, // do not render
    embed: (args: any) => <Embed {...args} />,
    iframe: (args: any) => <Iframe {...args} />,
    pre: (args: any) => {
      if (args.children.type === 'code') {
        const language = args.children.props.className?.replace('lang-', '')
        if (language === 'mermaid') {
          return <EmailMermaid graphDefinition={args.children.props.children} />
        }
        return (
          <EmailSyntaxHighlighter
            language={language}
            {...args.children.props}
          />
        )
      }
      return <></>
    },
  },
} as const

const EmailRender = (props: { article: RenderArticle }) => {
  return (
    <Markdown
      options={{
        ...opts,

        createElement: wrapStrictCreateElement({
          article: props.article,
        }),
      }}
    >
      {props.article.body}
    </Markdown>
  )
}

export default EmailRender

const EmailPoll = (props: { options: string[] }) => {
  return (
    <Container className="my-2 bg-green-300 p-8">
      <table className="w-full">
        {props.options.map((s) => (
          <tr key={s}>
            <td>{s}</td>
            <td className="text-right">123 votes (10%)</td>
          </tr>
        ))}
      </table>
    </Container>
  )
}
