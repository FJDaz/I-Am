// Diagnostic simple pour I-AMIENS
console.log("=== DIAGNOSTIC I-AMIENS ===");

// 1. Vérifier que le script se charge
console.log("✓ Script diagnostic chargé");

// 2. Vérifier l'URL
console.log("URL actuelle:", window.location.href);

// 3. Vérifier si l'overlay existe déjà
const existing = document.getElementById("amiens-assistant-overlay");
console.log("Overlay existant:", existing);

// 4. Attendre le DOM
setTimeout(() => {
  // 5. Chercher le bouton toggle
  const toggle = document.getElementById("assistant-toggle");
  console.log("Bouton toggle trouvé:", toggle);

  if (toggle) {
    console.log("✓ Bouton présent dans le DOM");
    console.log("  - Parent:", toggle.parentElement);
    console.log("  - Visible:", window.getComputedStyle(toggle).display);

    // 6. Tester le clic manuellement
    toggle.addEventListener("click", () => {
      console.log("✓ CLIC DÉTECTÉ SUR LE BOUTON!");
    });

    // 7. Vérifier les event listeners
    console.log("  - Event listeners attachés via script");
  } else {
    console.error("✗ Bouton toggle NON TROUVÉ dans le DOM");
    console.log("Éléments avec ID dans le body:",
      Array.from(document.querySelectorAll('[id]')).map(el => el.id)
    );
  }

  // 8. Vérifier l'overlay
  const overlay = document.getElementById("assistant-overlay");
  console.log("Overlay trouvé:", overlay);
}, 2000);
