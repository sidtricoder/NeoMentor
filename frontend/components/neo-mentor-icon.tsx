import { SVGProps } from 'react';

const NeoMentorIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="bg-transparent"
    {...props}
  >
    <path
      d="M12 2L2 7L12 12L22 7L12 2Z"
      fill="url(#paint0_linear)"
      stroke="url(#paint1_linear)"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M2 17L12 22L22 17"
      stroke="url(#paint2_linear)"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M2 12L12 17L22 12"
      stroke="url(#paint3_linear)"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient
        id="paint0_linear"
        x1="2"
        y1="7"
        x2="22"
        y2="7"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#3B82F6" />
        <stop offset="1" stopColor="#8B5CF6" />
      </linearGradient>
      <linearGradient
        id="paint1_linear"
        x1="2"
        y1="7"
        x2="22"
        y2="7"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#3B82F6" />
        <stop offset="1" stopColor="#8B5CF6" />
      </linearGradient>
      <linearGradient
        id="paint2_linear"
        x1="2"
        y1="19.5"
        x2="22"
        y2="19.5"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#3B82F6" />
        <stop offset="1" stopColor="#8B5CF6" />
      </linearGradient>
      <linearGradient
        id="paint3_linear"
        x1="2"
        y1="14.5"
        x2="22"
        y2="14.5"
        gradientUnits="userSpaceOnUse"
      >
        <stop stopColor="#3B82F6" />
        <stop offset="1" stopColor="#8B5CF6" />
      </linearGradient>
    </defs>
  </svg>
);

export default NeoMentorIcon;
