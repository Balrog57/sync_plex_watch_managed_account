from plexapi.server import PlexServer
import sys

# --- VOS INFORMATIONS ---
PLEX_URL = 'http://VOTRE_IP:32400'
PLEX_TOKEN = 'VOTRE_TOKEN_ADMIN'
USER_SOURCE = 'Nom_Compte_Source'   # Compte Admin (Source)
USER_TARGET = 'Nom_Compte_Cible'    # Utilisateur géré (Destination)
# ------------------------

print(f"--- Connexion au serveur {PLEX_URL} ---")
try:
    plex_admin = PlexServer(PLEX_URL, PLEX_TOKEN)
except Exception as e:
    print(f"Erreur de connexion : {e}")
    sys.exit(1)

print(f"--- Récupération du compte de : {USER_TARGET} ---")
try:
    # On récupère le compte admin global pour trouver l'utilisateur géré
    account = plex_admin.myPlexAccount()
    user_obj = account.user(USER_TARGET)
    # On obtient le token spécifique de Laurent pour ce serveur
    token_target = user_obj.get_token(plex_admin.machineIdentifier)
    # On se connecte en tant que Laurent
    plex_target = PlexServer(PLEX_URL, token_target)
except Exception as e:
    print(f"Impossible de trouver ou connecter l'utilisateur {USER_TARGET}. Vérifiez le nom exact.")
    print(f"Erreur : {e}")
    sys.exit(1)

print(f"--- Synchronisation de {USER_SOURCE} vers {USER_TARGET} ---")

# On parcourt toutes les bibliothèques
for section in plex_admin.library.sections():
    print(f"\nTraitement de la bibliothèque : {section.title} ({section.type})")
    
    # Stratégie : On ne récupère que ce qui a été touché (vus ou en cours) pour aller plus vite
    # Pour les films, c'est direct. Pour les séries, on cherche les EPISODES.
    
    items_to_sync = []
    
    if section.type == 'movie':
        items_to_sync = section.all() # On prend tout pour comparer
    elif section.type == 'show':
        # Astuce : on récupère directement tous les épisodes à plat
        items_to_sync = section.search(libtype='episode')
    else:
        print(f"  -> Type ignoré ({section.type})")
        continue

    count = 0
    for item_source in items_to_sync:
        # On ne s'intéresse qu'aux items VUS ou EN COURS
        if item_source.isPlayed or item_source.viewOffset > 0:
            try:
                # Recherche de l'équivalent chez Laurent
                # On utilise le ratingKey (ID unique) c'est plus fiable que le titre
                item_target = plex_target.fetchItem(item_source.ratingKey)
                
                # 1. Synchroniser le statut VU
                if item_source.isPlayed and not item_target.isPlayed:
                    item_target.markPlayed()
                    print(f"  [VU] {item_source.title}")
                    count += 1
                
                # 2. Synchroniser la position de lecture (En cours)
                elif item_source.viewOffset > 0:
                    # On évite de toucher si c'est déjà à peu près synchro (à 10s près)
                    if abs(item_target.viewOffset - item_source.viewOffset) > 10000:
                        item_target.updateProgress(item_source.viewOffset)
                        print(f"  [EN COURS] {item_source.title} -> {int(item_source.viewOffset/1000/60)} min")
                        count += 1
                        
            except Exception as e:
                # Si l'item n'existe pas ou erreur
                continue
    
    if count == 0:
        print("  -> Rien à synchroniser ici.")

print("\n--- TERMINE ! ---")