#!/usr/bin/env node
/**
 * Script de diagnostic pour l'extension Chrome
 * Vérifie les fichiers et identifie les problèmes
 */

const fs = require('fs');
const path = require('path');

const EXTENSION_DIR = __dirname;
const DATA_DIR = path.join(EXTENSION_DIR, 'data');

console.log('🔍 DIAGNOSTIC EXTENSION CHROME\n');
console.log('=' .repeat(60));

// 1. Vérifier les fichiers essentiels
console.log('\n📁 Vérification des fichiers...');
const requiredFiles = [
  'manifest.json',
  'content.js',
  'data/corpus_segments.json',
  'data/lexique_enfance.json',
  'data/questions_usager.json'
];

let allFilesOk = true;
for (const file of requiredFiles) {
  const filePath = path.join(EXTENSION_DIR, file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`  ✅ ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
  } else {
    console.log(`  ❌ ${file} - MANQUANT`);
    allFilesOk = false;
  }
}

// 2. Vérifier manifest.json
console.log('\n📋 Vérification manifest.json...');
try {
  const manifestPath = path.join(EXTENSION_DIR, 'manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  
  console.log(`  ✅ Version: ${manifest.version}`);
  console.log(`  ✅ Manifest version: ${manifest.manifest_version}`);
  
  // Vérifier les permissions
  if (manifest.host_permissions) {
    const hasLocalhost = manifest.host_permissions.some(p => p.includes('localhost:8711'));
    if (hasLocalhost) {
      console.log(`  ✅ Permissions localhost:8711 OK`);
    } else {
      console.log(`  ⚠️  Permissions localhost:8711 manquantes`);
    }
  }
  
  // Vérifier web_accessible_resources
  if (manifest.web_accessible_resources) {
    const resources = manifest.web_accessible_resources[0]?.resources || [];
    console.log(`  ✅ Web accessible resources: ${resources.length} fichiers`);
    
    // Vérifier que questions_usager.json est déclaré
    if (!resources.includes('data/questions_usager.json')) {
      console.log(`  ⚠️  questions_usager.json non déclaré dans web_accessible_resources`);
    }
  }
} catch (error) {
  console.log(`  ❌ Erreur parsing manifest.json: ${error.message}`);
  allFilesOk = false;
}

// 3. Vérifier content.js
console.log('\n📜 Vérification content.js...');
try {
  const contentPath = path.join(EXTENSION_DIR, 'content.js');
  const content = fs.readFileSync(contentPath, 'utf-8');
  
  // Vérifier la taille
  const sizeKB = (content.length / 1024).toFixed(2);
  console.log(`  ✅ Taille: ${sizeKB} KB`);
  
  // Vérifier les fonctions essentielles
  const requiredFunctions = [
    'normalizeQuestion',
    'rankSegments',
    'callAssistant',
    'handleSubmit',
    'loadSegments',
    'loadLexicon'
  ];
  
  for (const func of requiredFunctions) {
    if (content.includes(`function ${func}`) || content.includes(`${func}:`)) {
      console.log(`  ✅ Fonction ${func} présente`);
    } else {
      console.log(`  ⚠️  Fonction ${func} non trouvée`);
    }
  }
  
  // Vérifier l'endpoint
  if (content.includes('localhost:8711')) {
    console.log(`  ✅ Endpoint localhost:8711 trouvé`);
  } else {
    console.log(`  ⚠️  Endpoint localhost:8711 non trouvé`);
  }
  
  // Vérifier les erreurs de syntaxe basiques
  const openBraces = (content.match(/{/g) || []).length;
  const closeBraces = (content.match(/}/g) || []).length;
  if (openBraces === closeBraces) {
    console.log(`  ✅ Accolades équilibrées (${openBraces})`);
  } else {
    console.log(`  ❌ Accolades déséquilibrées (ouvrantes: ${openBraces}, fermantes: ${closeBraces})`);
    allFilesOk = false;
  }
  
} catch (error) {
  console.log(`  ❌ Erreur lecture content.js: ${error.message}`);
  allFilesOk = false;
}

// 4. Vérifier les données JSON
console.log('\n📊 Vérification des données JSON...');
const jsonFiles = [
  'data/corpus_segments.json',
  'data/lexique_enfance.json',
  'data/questions_usager.json'
];

for (const file of jsonFiles) {
  const filePath = path.join(EXTENSION_DIR, file);
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const data = JSON.parse(content);
    
    if (file.includes('corpus_segments')) {
      const count = Array.isArray(data) ? data.length : Object.keys(data).length;
      console.log(`  ✅ ${file}: ${count} segments`);
    } else if (file.includes('lexique')) {
      const entries = data.lexique_enfance || data;
      const count = Array.isArray(entries) ? entries.length : Object.keys(entries).length;
      console.log(`  ✅ ${file}: ${count} entrées`);
    } else if (file.includes('questions')) {
      const questions = data.questions || data;
      const count = Array.isArray(questions) ? questions.length : Object.keys(questions).length;
      console.log(`  ✅ ${file}: ${count} questions`);
    }
  } catch (error) {
    console.log(`  ❌ ${file}: Erreur JSON - ${error.message}`);
    allFilesOk = false;
  }
}

// 5. Résumé
console.log('\n' + '='.repeat(60));
if (allFilesOk) {
  console.log('✅ DIAGNOSTIC: Tous les fichiers semblent corrects');
  console.log('\n💡 Si l\'extension ne fonctionne pas:');
  console.log('   1. Vérifier la console du navigateur (F12)');
  console.log('   2. Vérifier que le serveur tourne sur localhost:8711');
  console.log('   3. Recharger l\'extension dans chrome://extensions');
} else {
  console.log('❌ DIAGNOSTIC: Problèmes détectés');
  console.log('\n🔧 Actions recommandées:');
  console.log('   1. Corriger les fichiers manquants ou corrompus');
  console.log('   2. Vérifier la syntaxe JSON');
  console.log('   3. Vérifier les permissions dans manifest.json');
}
console.log('='.repeat(60));

