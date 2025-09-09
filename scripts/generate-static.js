import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const distPath = path.join(__dirname, '..', 'dist');
const templatePath = path.join(__dirname, '..', 'viewer.html');

function generateStaticViewer(graphData) {
  // Read the original HTML template
  const template = fs.readFileSync(templatePath, 'utf-8');
  
  // Replace the placeholder with actual data
  const staticHTML = template.replace(
    '/*__GRAPH_JSON__*/',
    JSON.stringify(graphData, null, 2)
  );
  
  return staticHTML;
}

function copyStaticViewer() {
  try {
    // Check if dist directory exists
    if (!fs.existsSync(distPath)) {
      console.error('Dist directory not found. Please run "npm run build" first.');
      return;
    }

    // Copy the original viewer.html to dist as a fallback
    const originalViewerPath = path.join(__dirname, '..', 'viewer.html');
    const distViewerPath = path.join(distPath, 'viewer_legacy.html');
    
    if (fs.existsSync(originalViewerPath)) {
      fs.copyFileSync(originalViewerPath, distViewerPath);
      console.log('✅ Legacy viewer copied to dist/viewer_legacy.html');
    }

    // Create a sample graph.json file for testing
    const sampleGraphData = {
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
        }
      ]
    };

    // Write sample graph.json
    const graphJsonPath = path.join(distPath, 'graph.json');
    fs.writeFileSync(graphJsonPath, JSON.stringify(sampleGraphData, null, 2));
    console.log('✅ Sample graph.json created in dist/');

    // Generate static viewer with embedded data
    const staticHTML = generateStaticViewer(sampleGraphData);
    const staticViewerPath = path.join(distPath, 'viewer_static.html');
    fs.writeFileSync(staticViewerPath, staticHTML);
    console.log('✅ Static viewer with embedded data created at dist/viewer_static.html');

    console.log('\n📖 Usage:');
    console.log('- React development: npm run dev');
    console.log('- Production React: serve dist/index.html');
    console.log('- Legacy viewer: serve dist/viewer_legacy.html');
    console.log('- Static viewer: serve dist/viewer_static.html');

  } catch (error) {
    console.error('❌ Error generating static files:', error);
  }
}

copyStaticViewer();