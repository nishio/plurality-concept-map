import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const docsPath = path.join(__dirname, '..', '..', 'docs');
const distPath = path.join(__dirname, '..', 'dist');

function copyToDocsDirectory() {
  try {
    // Check if dist directory exists
    if (!fs.existsSync(distPath)) {
      console.error('Dist directory not found. Please run "npm run build" first.');
      return;
    }

    // Create docs directory if it doesn't exist
    if (!fs.existsSync(docsPath)) {
      fs.mkdirSync(docsPath, { recursive: true });
      console.log('✅ Created docs/ directory');
    }

    // Copy all files from dist to docs
    const distFiles = fs.readdirSync(distPath);
    
    for (const file of distFiles) {
      const sourcePath = path.join(distPath, file);
      const destPath = path.join(docsPath, file);
      
      if (fs.lstatSync(sourcePath).isDirectory()) {
        // Copy directory recursively
        fs.cpSync(sourcePath, destPath, { recursive: true });
      } else {
        // Copy file
        fs.copyFileSync(sourcePath, destPath);
      }
    }

    // Load actual graph data from public/graph.json and copy to docs
    const publicGraphPath = path.join(__dirname, '..', 'public', 'graph.json');
    
    if (fs.existsSync(publicGraphPath)) {
      try {
        const graphContent = fs.readFileSync(publicGraphPath, 'utf-8');
        const graphData = JSON.parse(graphContent);
        
        // Write graph.json to docs
        const docsGraphPath = path.join(docsPath, 'graph.json');
        fs.writeFileSync(docsGraphPath, JSON.stringify(graphData, null, 2));
        console.log('✅ Graph.json copied to docs/');
      } catch (error) {
        console.error('❌ Error reading graph.json:', error);
      }
    } else {
      console.warn('⚠️ No graph.json found in public/, using empty data');
      const emptyData = { nodes: [], edges: [] };
      const docsGraphPath = path.join(docsPath, 'graph.json');
      fs.writeFileSync(docsGraphPath, JSON.stringify(emptyData, null, 2));
      console.log('✅ Empty graph.json created in docs/');
    }

    console.log('✅ SPA static build copied to docs/ directory');
    console.log('\n📖 Usage:');
    console.log('- GitHub Pages: Push docs/ directory to repository');
    console.log('- Local testing: serve docs/index.html');

  } catch (error) {
    console.error('❌ Error copying to docs directory:', error);
  }
}

copyToDocsDirectory();