import type { Meta, StoryObj } from '@storybook/react'

import PledgeCheckoutFundOnCompletion from './PledgeCheckoutFundOnCompletion'

import { issue } from 'polarkit/testdata'

const meta: Meta<typeof PledgeCheckoutFundOnCompletion> = {
  title: 'Organisms/PledgeCheckoutFundOnCompletion',
  component: PledgeCheckoutFundOnCompletion,
  tags: ['autodocs'],
  parameters: {
    themes: ['light', 'dark'],
    nextjs: {
      appDirectory: true,
    },
  },
  render: (args) => (
    <div className="max-w-[400px]">
      <PledgeCheckoutFundOnCompletion {...args} />
    </div>
  ),
}

export default meta

type Story = StoryObj<typeof PledgeCheckoutFundOnCompletion>

export const Default: Story = {
  args: {
    issue: issue,
  },
}
