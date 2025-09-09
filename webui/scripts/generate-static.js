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

    // Load actual graph data from public/graph.json
    const publicGraphPath = path.join(__dirname, '..', 'public', 'graph.json');
    let graphData;
    
    if (fs.existsSync(publicGraphPath)) {
      try {
        const graphContent = fs.readFileSync(publicGraphPath, 'utf-8');
        graphData = JSON.parse(graphContent);
        console.log('✅ Loaded actual graph data from public/graph.json');
      } catch (error) {
        console.error('❌ Error reading graph.json:', error);
        graphData = { nodes: [], edges: [] };
      }
    } else {
      console.warn('⚠️ No graph.json found in public/, using empty data');
      graphData = { nodes: [], edges: [] };
    }

    // Write graph.json to dist
    const graphJsonPath = path.join(distPath, 'graph.json');
    fs.writeFileSync(graphJsonPath, JSON.stringify(graphData, null, 2));
    console.log('✅ Graph.json copied to dist/');

    // Generate static viewer with embedded data
    const staticHTML = generateStaticViewer(graphData);
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