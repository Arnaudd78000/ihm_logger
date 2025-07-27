# File: ihm_logger.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import datetime # Importation nécessaire pour la gestion du temps
import tkinter.font as tkfont # Importation pour gérer les polices

# Couleurs thème sombre
BG_COLOR = "#2f2f2f"     # gris foncé
FG_COLOR = "white"       # texte blanc
BTN_BG = "#444444"       # bouton un peu plus clair
BTN_FG = "white"
REFRESH_BTN_BG = "#90EE90" # Vert clair pour le bouton rafraîchir
REFRESH_BTN_FG = "black" # Texte noir pour le bouton rafraîchir (meilleur contraste)


# Palette de couleurs pour les préfixes
COLOR_PALETTE = [

    "#00FF00", # Vert
    "#0000FF", # Bleu
    "#FFFF00", # Jaune
    "#FF00FF", # Magenta
    "#00FFFF", # Cyan
    "#FFA500", # Orange
    "#800080", # Violet
    "#808000", # Olive
    "#8B4513",  # Marron
    "#FF0000" # Rouge
]

# Variable globale pour stocker le contenu complet du fichier actuel
contenu_fichier_actuel = ""
# Variable globale pour stocker le chemin du fichier actuel
chemin_fichier_actuel = ""


def charger_options(chemin):
    try:
        with open(chemin, "r") as f:
            lignes = [ligne.strip() for ligne in f.readlines() if ligne.strip()]
        return lignes
    except FileNotFoundError:
        return []

def mettre_a_jour_menus(options):
    options_modifiees = ["Tout", "Aucune sélection"] + options if options else ["Tout", "Aucune sélection"]

    for i, val in enumerate([val1, val2, val3]):
        val.set("Tout" if i == 0 else "Aucune sélection")

        menu = menus[i]["menu"]
        menu.delete(0, "end")
        for option in options_modifiees:
            menu.add_command(label=option, command=lambda v=val, o=option: v.set(o))

def appliquer_filtre_et_afficher(*args):
    """Applique les filtres (options et heure) au contenu actuel et met à jour l'affichage."""
    global contenu_fichier_actuel
    if not contenu_fichier_actuel:
        # Si aucun fichier n'est chargé, vider le widget texte
        texte_widget.config(state=tk.NORMAL)
        texte_widget.delete(1.0, tk.END)
        texte_widget.config(state=tk.DISABLED)
        return

    # --- Récupérer et parser les heures de début et de fin ---
    debut_str = val_heure_debut.get().strip()
    fin_str = val_heure_fin.get().strip()
    debut_time = None
    fin_time = None
    heure_filtre_actif = False # Flag pour savoir si un filtre horaire est appliqué

    if debut_str:
        heure_filtre_actif = True
        try:
            # Tente de parser hh:mm
            debut_time = datetime.datetime.strptime(debut_str, '%H:%M').time()
        except ValueError:
            # Gérer l'erreur de format si nécessaire (pour l'instant, on ignore le filtre si format invalide)
            #print(f"Format d'heure de début invalide: {debut_str}")
            debut_time = None # Invalider le filtre si le format est incorrect

    if fin_str:
        heure_filtre_actif = True
        try:
            # Tente de parser hh:mm
            fin_time = datetime.datetime.strptime(fin_str, '%H:%M').time()
        except ValueError:
            # Gérer l'erreur de format si nécessaire
            print(f"Format d'heure de fin invalide: {fin_str}")
            fin_time = None # Invalider le filtre si le format est incorrect

    # --- Construire la liste des préfixes de filtre (logique existante) ---
    filtre1_val = val1.get()
    filtre2_val = val2.get()
    filtre3_val = val3.get()

    # Vérifier si "Tout" est sélectionné dans n'importe quel filtre de préfixe
    tout_prefixe_selectionne = "Tout" in [filtre1_val, filtre2_val, filtre3_val]

    prefixes_filtre = []
    if not tout_prefixe_selectionne:
        for val in [filtre1_val, filtre2_val, filtre3_val]:
            if val != "Aucune sélection":
                index_colon = val.find(':')
                if index_colon != -1:
                    prefix = val[:index_colon]
                    prefixes_filtre.append(prefix)
                else:
                     prefixes_filtre.append(val)

    # --- Appliquer les filtres ---
    lignes = contenu_fichier_actuel.splitlines()
    lignes_filtrees = []

    for ligne in lignes:
        # --- Appliquer le filtre de préfixe ---
        ligne_passe_prefixe_filtre = False
        if tout_prefixe_selectionne:
            ligne_passe_prefixe_filtre = True
        elif not prefixes_filtre:
             # Si aucun filtre de préfixe actif (tous "Aucune sélection"), la ligne ne passe pas
             ligne_passe_prefixe_filtre = False
        else:
            # Vérifier si la ligne commence par un des préfixes actifs
            # Utiliser strip() pour ignorer les espaces/tabulations en début de ligne
            if any(ligne.strip().startswith(prefix) for prefix in prefixes_filtre):
                ligne_passe_prefixe_filtre = True

        # --- Appliquer le filtre horaire si actif ---
        ligne_passe_heure_filtre = True # Par default, la ligne passe le filtre horaire si aucun filtre horaire n'est actif

        if heure_filtre_actif:
            ligne_time = None
            # Extraire et parser l'heure de la ligne
            try:
                # Rechercher la première occurrence de '['
                debut_crochet = ligne.find('[')
                if debut_crochet != -1:
                    # Rechercher la première occurrence de ']' après '['
                    fin_crochet = ligne.find(']', debut_crochet)
                    if fin_crochet != -1:
                        # Extraire la chaîne entre '[' et ']'
                        time_str_in_brackets = ligne[debut_crochet + 1:fin_crochet]
                        # Tenter de parser hh:mm:ss d'abord
                        try:
                            ligne_time = datetime.datetime.strptime(time_str_in_brackets, '%H:%M:%S').time()
                        except ValueError:
                            # Si hh:mm:ss échoue, tenter hh:mm
                            try:
                                ligne_time = datetime.datetime.strptime(time_str_in_brackets, '%H:%M').time()
                            except ValueError:
                                # Si aucun format ne correspond, ligne_time reste None
                                pass
            except Exception as e:
                 # Gérer d'autres erreurs potentielles lors de l'extraction/parsing
                 print(f"Erreur lors de l'extraction/parsing de l'heure sur la ligne: {ligne[:50]}... Erreur: {e}")
                 ligne_time = None # Assurer que ligne_time est None en cas d'erreur

            # Appliquer les conditions de filtre horaire
            if ligne_time is None:
                # Si la ligne n'a pas d'heure parsable, elle ne passe pas le filtre horaire si un filtre horaire est actif
                 ligne_passe_heure_filtre = False
            else:
                if debut_time is not None and ligne_time < debut_time:
                    ligne_passe_heure_filtre = False
                if fin_time is not None and ligne_time > fin_time:
                    ligne_passe_heure_filtre = False


        # La ligne est conservée si elle passe le filtre de préfixe ET le filtre horaire
        if ligne_passe_prefixe_filtre and ligne_passe_heure_filtre:
            lignes_filtrees.append(ligne)


    # --- Mettre à jour l'affichage avec coloration ---
    texte_widget.config(state=tk.NORMAL)
    texte_widget.delete(1.0, tk.END)

    for ligne in lignes_filtrees:
        tag_name = None
        # Déterminer le tag (couleur) basé sur le préfixe
        for i in range(len(COLOR_PALETTE)):
            prefix_to_match = f"F{i}"
            if ligne.strip().startswith(prefix_to_match):
                tag_name = f"color{i}"
                break # On prend le premier préfixe correspondant

        if tag_name:
            texte_widget.insert(tk.END, ligne + "\n", tag_name)
        else:
            # Si aucun préfixe Fx ne correspond, insérer avec la couleur par défaut
            texte_widget.insert(tk.END, ligne + "\n")

    texte_widget.config(state=tk.DISABLED)


def choisir_fichier():
    global contenu_fichier_actuel
    global chemin_fichier_actuel # Déclarer la variable globale
    # Choix du dossier initial selon le logger
    if val_logger.get() == "ihm_q":
        dossier_initial = "/home/arnaud/Bureau/RASADA/AAA_Projects/LOG/ihm_q_log_files/"
    else :
        dossier_initial = "/media/Rasada_MyUsb/LOG/"+ val_logger.get()
    print(dossier_initial)
    fichier = filedialog.askopenfilename(
        initialdir=dossier_initial,
        filetypes=[("Fichiers LOG", "*.log")]
    )
    if fichier:
        chemin_fichier_actuel = fichier # Stocker le chemin du fichier
        nom_fichier = os.path.basename(fichier)
        label_nom_fichier.config(text=nom_fichier)

        dossier_parent = os.path.basename(os.path.dirname(fichier))
        # Adapter chemin_options selon le logger
        print(val_logger.get())
        if val_logger.get() == "ihm_q":
            chemin_options = f"/home/arnaud/Bureau/RASADA/AAA_Projects/LOG/fonction_log_{dossier_parent}.txt"
        else:
            chemin_options = f"/media/Rasada_MyUsb/LOG/fonction_log_{dossier_parent}.txt"

        options = charger_options(chemin_options)

        if not options:
            messagebox.showwarning("Fichier introuvable", f"Fichier non trouvé ou vide :\n{chemin_options}")

        mettre_a_jour_menus(options)

        # Lire le contenu complet et le stocker
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                contenu_fichier_actuel = f.read()

            # Appliquer le filtre initial et afficher
            appliquer_filtre_et_afficher()

        except Exception as e:
            contenu_fichier_actuel = "" # Vider le contenu en cas d'erreur
            texte_widget.config(state=tk.NORMAL)
            texte_widget.delete(1.0, tk.END)
            texte_widget.insert(tk.END, f"Erreur lors de la lecture du fichier :\n{e}")
            texte_widget.config(state=tk.DISABLED)

# Nouvelle fonction pour rafraîchir le fichier
def rafraichir_fichier():
    global contenu_fichier_actuel
    global chemin_fichier_actuel
    if chemin_fichier_actuel: # Vérifier si un fichier est chargé
        try:
            with open(chemin_fichier_actuel, "r", encoding="utf-8") as f:
                contenu_fichier_actuel = f.read()
            appliquer_filtre_et_afficher() # Réappliquer les filtres et afficher
        except Exception as e:
            # Gérer l'erreur lors du rafraîchissement
            contenu_fichier_actuel = ""
            texte_widget.config(state=tk.NORMAL)
            texte_widget.delete(1.0, tk.END)
            texte_widget.insert(tk.END, f"Erreur lors du rafraîchissement du fichier :\n{e}")
            texte_widget.config(state=tk.DISABLED)
            messagebox.showerror("Erreur de rafraîchissement", f"Impossible de rafraîchir le fichier :\n{e}")
    # else: # Optionnel : informer l'utilisateur qu'aucun fichier n'est chargé
    #     messagebox.showinfo("Information", "Aucun fichier n'est actuellement chargé.")


def charger_fichier_recent():
    global contenu_fichier_actuel
    global chemin_fichier_actuel
    # Déterminer le dossier selon val_logger
    if val_logger.get() == "ihm_q":
        dossier = "/home/arnaud/Bureau/RASADA/AAA_Projects/LOG/ihm_q_log_files/"
    elif val_logger.get() == "nodered":
        dossier = "/media/Rasada_MyUsb/LOG/nodered"
    elif val_logger.get() == "nodered_garage":
        dossier = "/media/Rasada_MyUsb/LOG/nodered_garage"
    elif val_logger.get() == "ihm_sdb_log_files":
        dossier = "/media/Rasada_MyUsb/LOG/ihm_sdb_log_files"
    else:
        dossier = "/media/Rasada_MyUsb/LOG/"
    try:
        fichiers = [os.path.join(dossier, f) for f in os.listdir(dossier) if f.endswith('.log')]
        if not fichiers:
            messagebox.showwarning("Aucun fichier log", f"Aucun fichier .log trouvé dans {dossier}")
            return
        fichier_recent = max(fichiers, key=os.path.getmtime)
        chemin_fichier_actuel = fichier_recent
        nom_fichier = os.path.basename(fichier_recent)
        label_nom_fichier.config(text=nom_fichier)
        dossier_parent = os.path.basename(os.path.dirname(fichier_recent))
        # Adapter chemin_options selon le logger
        if val_logger.get() == "ihm_q":
            chemin_options = f"/home/arnaud/Bureau/RASADA/AAA_Projects/LOG/fonction_log_{dossier_parent}.txt"
        else:
            chemin_options = f"/media/Rasada_MyUsb/LOG/fonction_log_{dossier_parent}.txt"
        options = charger_options(chemin_options)
        if not options:
            messagebox.showwarning("Fichier introuvable", f"Fichier non trouvé ou vide :\n{chemin_options}")
        mettre_a_jour_menus(options)
        # Lire le contenu complet et le stocker
        with open(fichier_recent, "r", encoding="utf-8") as f:
            contenu_fichier_actuel = f.read()
        appliquer_filtre_et_afficher()
    except Exception as e:
        contenu_fichier_actuel = ""
        texte_widget.config(state=tk.NORMAL)
        texte_widget.delete(1.0, tk.END)
        texte_widget.insert(tk.END, f"Erreur lors de la lecture du fichier :\n{e}")
        texte_widget.config(state=tk.DISABLED)


root = tk.Tk()
root.title("IHM LOGGER")
root.geometry("800x1000+1100+0") # Positionner la fenêtre à 400 pixels du haut de l'écran
root.configure(bg=BG_COLOR)
root.iconphoto(False, tk.PhotoImage(file='/home/arnaud/Bureau/RASADA/AAA_Projects/ihm_logger/log_icon.png'))


# Définir une police plus grande pour le bouton de rafraîchissement
refresh_font = tkfont.Font(size=16) # Ajustez la taille selon vos besoins

# Ajout du choix du logger (PC ou Réseau) avec boutons radio de même taille
frame_logger = tk.Frame(root, bg=BG_COLOR)
frame_logger.pack(fill="x", padx=10, pady=8)

label_logger = tk.Label(frame_logger, text="Logger :", bg=BG_COLOR, fg=FG_COLOR)
label_logger.pack(side="left", padx=5)

val_logger = tk.StringVar(value="ihm_q")
radio_width = 12  # Largeur identique pour les deux boutons radio
radio_pc = tk.Radiobutton(frame_logger, text="ihm_Q", variable=val_logger, value="ihm_q", width=radio_width, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=FG_COLOR)
radio_pc.pack(side="left", padx=5)
radio_nodered = tk.Radiobutton(frame_logger, text="Nodered Ras", variable=val_logger, value="nodered", width=radio_width, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=FG_COLOR)
radio_nodered.pack(side="left", padx=5)
radio_nodered_gar = tk.Radiobutton(frame_logger, text="Nodered Gar", variable=val_logger, value="nodered_garage", width=radio_width, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=FG_COLOR)
radio_nodered_gar.pack(side="left", padx=5)
radio_nodered_sdb = tk.Radiobutton(frame_logger, text="ihm_SdB", variable=val_logger, value="ihm_sdb_log_files", width=radio_width, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=FG_COLOR)
radio_nodered_sdb.pack(side="left", padx=5)

# Ligne 1 : Choix de fichier
frame_fichier = tk.Frame(root, bg=BG_COLOR)
frame_fichier.pack(fill="x", padx=10, pady=2)

btn_choisir = tk.Button(frame_fichier, text="Choisir un fichier", command=choisir_fichier,
                        bg=BTN_BG, fg=BTN_FG, activebackground="#555555", activeforeground=FG_COLOR,
                        relief="raised")
btn_choisir.pack(side="left", padx=5, pady=2)

label_nom_fichier = tk.Label(frame_fichier, text="", bg="white", fg="black", anchor="w")
label_nom_fichier.pack(side="left", fill="x", expand=True, padx=5, pady=2)

# Nouvelle section pour le champ de saisie de l'heure de début et de fin
frame_heure_debut = tk.Frame(root, bg=BG_COLOR)
frame_heure_debut.pack(fill="x", padx=10, pady=2)

label_heure_debut = tk.Label(frame_heure_debut, text="Début (hh:mm):", bg=BG_COLOR, fg=FG_COLOR)
label_heure_debut.pack(side="left", padx=5)

val_heure_debut = tk.StringVar() # Variable pour stocker l'heure saisie
entry_heure_debut = tk.Entry(frame_heure_debut, textvariable=val_heure_debut, width=10, bg="#444444", fg=FG_COLOR, insertbackground="white")
entry_heure_debut.pack(side="left", padx=5)

# Lier le changement de valeur du champ de saisie à la fonction de mise à jour de l'affichage
val_heure_debut.trace_add('write', appliquer_filtre_et_afficher)

# Ajout du label et du champ de saisie pour l'heure de fin
label_heure_fin = tk.Label(frame_heure_debut, text="Fin (hh:mm):", bg=BG_COLOR, fg=FG_COLOR)
label_heure_fin.pack(side="left", padx=5)

val_heure_fin = tk.StringVar() # Variable pour stocker l'heure de fin saisie
entry_heure_fin = tk.Entry(frame_heure_debut, textvariable=val_heure_fin, width=10, bg="#444444", fg=FG_COLOR, insertbackground="white")
entry_heure_fin.pack(side="left", padx=5)

# Lier le changement de valeur du champ de saisie de fin à la fonction de mise à jour de l'affichage
val_heure_fin.trace_add('write', appliquer_filtre_et_afficher)

# Ajout du bouton de rafraîchissement
btn_rafraichir = tk.Button(frame_heure_debut, text="↻", command=rafraichir_fichier,
                           bg=REFRESH_BTN_BG, fg=REFRESH_BTN_FG, activebackground="#7CFC00", activeforeground="black", # Vert plus vif au clic
                           relief="raised", width=9, font=refresh_font) # Augmentation de la largeur et application de la police
btn_rafraichir.pack(side="right", padx=5) # Placer le bouton à droite

val1 = tk.StringVar(value="Tout")
val2 = tk.StringVar(value="Aucune sélection")
val3 = tk.StringVar(value="Aucune sélection")
menus = []

for val in [val1, val2, val3]:
    frame_menu = tk.Frame(root, bg=BG_COLOR)
    frame_menu.pack(fill="x", padx=10, pady=2)

    option_menu = tk.OptionMenu(frame_menu, val, "Tout", "Aucune sélection")
    option_menu.config(width=100, anchor="w", bg=BG_COLOR, fg=FG_COLOR, relief="flat")
    option_menu["menu"].config(bg=BG_COLOR, fg=FG_COLOR)
    option_menu.pack(fill="x")
    menus.append(option_menu)
    # Lier le changement de valeur à la fonction de mise à jour de l'affichage
    val.trace_add('write', appliquer_filtre_et_afficher)


# Widget pour afficher le contenu du fichier
texte_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#1e1e1e", fg="#cccccc", insertbackground="white")
texte_widget.pack(expand=True, fill="both", padx=10, pady=10)
texte_widget.config(state=tk.DISABLED) # Rendre le widget en lecture seule par défaut

# Configurer les tags pour la coloration
for i, color in enumerate(COLOR_PALETTE):
    texte_widget.tag_config(f"color{i}", foreground=color)

val_logger.trace_add('write', lambda *args: charger_fichier_recent())

root.mainloop()