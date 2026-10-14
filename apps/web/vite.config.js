import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from 'node:fs';

export default defineConfig({
  plugins: [react(), { name:'lotus-offline-shell',generateBundle(options,bundle){ this.emitFile({type:'asset',fileName:'sw.js',source:readFileSync(new URL('./public/sw.js',import.meta.url),'utf8').replace('__ASSET_LIST__',JSON.stringify(Object.keys(bundle).filter(n=>n.startsWith('assets/')).map(n=>'/'+n)))}); } }],
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8787' } },
});
