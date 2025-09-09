import { GraphData } from '../types';

export const sampleData: GraphData = {
  "nodes": [
    {
      "id": "plurality",
      "label": "プラリティ",
      "definition": "多様性と協力を両立させる社会技術の概念",
      "tier": "core",
      "aliases": ["多様性協力", "Plurality"],
      "evidence": [
        {
          "text": "プラリティは、多様性と協力という一見矛盾する要素を技術によって両立させることを目指す概念です。",
          "section": "第1章"
        }
      ]
    },
    {
      "id": "digital_democracy", 
      "label": "デジタル民主主義",
      "definition": "デジタル技術を活用した民主的意思決定の仕組み",
      "tier": "supplementary",
      "aliases": ["電子民主主義", "Digital Democracy"],
      "evidence": [
        {
          "text": "デジタル民主主義は、インターネットやAIを活用して、より多くの人々が政治プロセスに参加できる仕組みを作ります。",
          "section": "第2章"
        }
      ]
    },
    {
      "id": "quadratic_voting",
      "label": "二次投票",
      "definition": "投票コストが票数の二乗に比例する投票制度",
      "tier": "advanced",
      "aliases": ["QV", "Quadratic Voting"],
      "evidence": [
        {
          "text": "二次投票では、より多くの票を投じるほどコストが二次関数的に増加し、強い選好を持つ意見により大きな重みを与えます。",
          "section": "第3章"
        }
      ]
    }
  ],
  "edges": [
    {
      "source": "digital_democracy",
      "target": "plurality", 
      "type": "part_of",
      "confidence": 0.9,
      "evidence": [
        {
          "text": "デジタル民主主義は、プラリティの実現手段の一つとして重要な役割を果たします。"
        }
      ]
    },
    {
      "source": "quadratic_voting",
      "target": "digital_democracy",
      "type": "example_of", 
      "confidence": 0.8,
      "evidence": [
        {
          "text": "二次投票は、デジタル民主主義の具体的な実装例として注目されています。"
        }
      ]
    }
  ]
};