-- Sous-titres des cinematiques de Welcome to the Game III.
--
-- Le jeu n'a aucun systeme de sous-titres et ses paquets ne peuvent pas en
-- recevoir (serialisation unversioned, bSubtitlesEnabled transient) : le texte
-- est donc affiche par du code, a l'execution.
--
-- Deux moities independantes :
--   detection  -- on sonde les UAudioComponent : des que l'un joue un des
--                 SoundWave de voix, on demarre la piste correspondante ;
--   affichage  -- un widget UMG (CanvasPanel + TextBlock) bati a l'execution
--                 et pose dans le viewport.
--
-- La voie AHUD:DrawText a ete essayee et abandonnee : le hook sur
-- ReceiveDrawHUD s'enregistre bien, mais les HUD Blueprints du jeu
-- (BP_TitleHUD, BP_ApartmentGameHUD...) n'implementent pas l'evenement, qui
-- n'est donc jamais appele. Tout l'affichage du jeu passe par UMG.
--
-- Le minutage vient des .srt poses a cote (dossier SousTitres/), lus au
-- demarrage. Aucun asset n'est touche : une mise a jour Steam ne casse rien.

local INTERVALLE = 100      -- ms entre deux sondages des composants audio

-- Journalisation : muette en usage normal. La passer a true fait dire au mod
-- ce qu'il repere, ce qu'il joue et ou sa construction s'arrete — c'est le
-- seul diagnostic possible, ce build shipping n'ecrivant aucun log a lui.
local DIAG = false

-- Repere du dossier du mod, deduit du chemin de ce fichier.
local source = debug.getinfo(1, "S").source:sub(2)
local RACINE = source:match("^(.*)[/\\]Scripts[/\\][^/\\]+$") or "."

-- Nom du son joue -> fichier de sous-titres.
--
-- Deux formes coexistent. Le jeu joue l'intro par un MetaSound qui enveloppe
-- le SoundWave : a l'execution on voit « MS_WadeIntro », jamais
-- « Wade_MotelIntro-Full ». Seules l'intro et la replique de Tanner ont une
-- telle enveloppe dans le pak ; les deux fins se jouent sous leur propre nom.
-- On accepte les deux formes, ce qui couvre aussi un changement de montage.
-- Regle generale : un son « Truc » est sous-titre par « Truc.srt ». Les
-- exceptions ci-dessous sont les enveloppes MetaSound, qui portent un autre
-- nom que le fichier. La liste des sons sous-titres est celle des .srt
-- presents dans SousTitres\, lue au demarrage : ajouter une voix ne demande
-- que d'y deposer un fichier.
local ENVELOPPES = {
    ["MS_WadeIntro"] = "Wade_MotelIntro-Full",
    ["MS_Tanner_NoFun"] = "Tanner_NoFun",
    -- L'appartement de Simon : le proprietaire derriere la porte. Le journal
    -- ne montre que ces noms-la, jamais les SFX_ qu'ils enveloppent.
    ["MS_FinalNotice"] = "SFX_FinalNotice",
    ["MS_SimonA"] = "SFX_SimonA",
    ["MS_SimonB"] = "SFX_SimonB",
    ["MS_PapersUnderDoor"] = "SFX_PapersUnderDoor",
}

local textes = {}           -- nom du son -> liste de repliques {debut, fin, texte}
local courant = nil         -- {nom, t0, repliques, composant}
local police = nil          -- UFont resolu une fois
local essai_jusqua = 0      -- horodatage de fin de la ligne d'essai (touche F9)
local diag_tour = 0

local function log(msg)
    print("[SousTitresFR] " .. msg .. "\n")
end

-- ---------------------------------------------------------------- lecture srt

local function horodatage(s)
    local h, m, sec, ms = s:match("(%d+):(%d+):(%d+)[,%.](%d+)")
    if not h then return nil end
    return ((tonumber(h) * 60 + tonumber(m)) * 60 + tonumber(sec)) + tonumber(ms) / 1000
end

local function lire_srt(chemin)
    local f = io.open(chemin, "rb")
    if not f then return nil end
    local brut = f:read("*a")
    f:close()
    -- Les .srt sont ecrits en UTF-8 ; on retire l'eventuel BOM.
    brut = brut:gsub("^\239\187\191", ""):gsub("\r\n", "\n")

    local repliques = {}
    for bloc in (brut .. "\n\n"):gmatch("(.-)\n\n") do
        local lignes = {}
        for l in bloc:gmatch("[^\n]+") do lignes[#lignes + 1] = l end
        local i = 1
        if lignes[1] and lignes[1]:match("^%s*%d+%s*$") then i = 2 end
        local minutage = lignes[i]
        if minutage and minutage:find("%-%->") then
            local a, b = minutage:match("(.-)%s*%-%->%s*(.*)")
            local debut, fin = horodatage(a or ""), horodatage(b or "")
            local texte = table.concat(lignes, "\n", i + 1)
            if debut and fin and texte ~= "" then
                repliques[#repliques + 1] = { debut = debut, fin = fin, texte = texte }
            end
        end
    end
    return repliques
end

-- Lister un dossier depuis Lua sans bibliotheque : on passe par le shell, une
-- seule fois au demarrage. `dir /b` donne un nom par ligne, sans fioriture.
local function lister_srt(dossier)
    local noms = {}
    local tube = io.popen('dir /b "' .. dossier .. '\\*.srt" 2>nul')
    if not tube then return noms end
    for ligne in tube:lines() do
        local nom = ligne:match("^%s*(.-)%s*$")
        if nom ~= "" then noms[#noms + 1] = nom end
    end
    tube:close()
    return noms
end

local function charger()
    local dossier = RACINE .. "\\SousTitres"
    local par_base, total, fichiers = {}, 0, 0

    for _, fichier in ipairs(lister_srt(dossier)) do
        local base = fichier:gsub("%.[sS][rR][tT]$", "")
        local repliques = lire_srt(dossier .. "\\" .. fichier)
        if repliques and #repliques > 0 then
            par_base[base] = repliques
            textes[base] = repliques
            total = total + #repliques
            fichiers = fichiers + 1
        else
            log("sous-titres illisibles ou vides : " .. fichier)
        end
    end

    -- Les enveloppes MetaSound partagent la liste de leur SoundWave.
    for enveloppe, base in pairs(ENVELOPPES) do
        if par_base[base] then textes[enveloppe] = par_base[base] end
    end

    log(("charge : %d repliques, %d fichiers"):format(total, fichiers))
end

-- ------------------------------------------------------------------ detection

-- Horloge. Surtout pas os.clock() : en Lua il rend le temps *processeur* du
-- processus, pas le temps mural. Dans un jeu multithread il avance beaucoup
-- plus vite que la realite — les sous-titres defilaient trop vite — et il
-- continue d'avancer a l'arret, le moteur continuant de calculer.
--
-- On prend donc l'horloge audio du moteur, qui a deux vertus : elle est murale,
-- et elle gele quand le son est suspendu, donc a la pause. Repli sur l'horloge
-- du monde, puis sur os.clock faute de mieux.
local gameplay_statics = nil
local contexte_monde = nil
local voie_horloge = nil

local function statics()
    if gameplay_statics and gameplay_statics:IsValid() then return gameplay_statics end
    local o = StaticFindObject("/Script/Engine.Default__GameplayStatics")
    if o and o:IsValid() then gameplay_statics = o end
    return gameplay_statics
end

-- Le contexte est garde en memoire : l'horloge est lue plusieurs fois par tour
-- et rechercher le PlayerController a chaque fois multiplierait sans raison les
-- appels d'UFunction, la source des plantages de ce mod.
local function contexte()
    if contexte_monde and contexte_monde:IsValid() then return contexte_monde end
    local pc = FindFirstOf("PlayerController")
    contexte_monde = (pc and pc:IsValid()) and pc or nil
    return contexte_monde
end

-- Repli : un compteur avance d'un pas a chaque tour de la boucle principale,
-- qui tourne toutes les INTERVALLE millisecondes de temps reel. C'est
-- grossier, mais c'est du temps mural — contrairement a os.clock, qui rend le
-- temps processeur et courait plusieurs fois trop vite.
local tic = 0

local function noter_voie(nom)
    if voie_horloge ~= nom then
        voie_horloge = nom
        if DIAG then log("horloge : " .. nom) end
    end
end

local function maintenant()
    local lib = statics()
    if not lib then
        noter_voie("compteur (GameplayStatics introuvable)")
        return tic
    end
    local ctx = contexte()
    if not ctx then
        noter_voie("compteur (pas de contexte de monde)")
        return tic
    end
    for _, methode in ipairs({ "GetAudioTimeSeconds", "GetTimeSeconds" }) do
        local ok, t = pcall(function() return lib[methode](lib, ctx) end)
        if ok and type(t) == "number" and t > 0 then
            noter_voie(methode)
            return t
        end
        if DIAG and not ok and voie_horloge ~= "echec " .. methode then
            log("horloge : " .. methode .. " refuse — " .. tostring(t))
        end
    end
    noter_voie("compteur (appels refuses)")
    return tic
end

local function nom_du_son(composant)
    local ok, nom = pcall(function()
        local son = composant.Sound
        if not son or not son:IsValid() then return nil end
        return son:GetFName():ToString()
    end)
    if not ok then return nil end
    return nom
end

-- EAudioComponentPlayState : 0 Playing, 1 Stopped, 2 Paused, 3 FadingIn,
-- 4 FadingOut. Rendu nil si l'appel echoue, auquel cas on se rabat sur
-- IsPlaying, qui ne distingue pas la pause.
local function etat_lecture(composant)
    local ok, res = pcall(function() return composant:GetPlayState() end)
    if not ok or res == nil then return nil end
    return tonumber(res)
end

local function fin_de_piste(repliques)
    local fin = 0
    for _, r in ipairs(repliques) do
        if r.fin > fin then fin = r.fin end
    end
    return fin
end

local function demarrer(nom, composant)
    courant = {
        nom = nom,
        repliques = textes[nom],
        composant = composant,
        ecoule = 0,               -- temps de lecture reel, pause deduite
        dernier = maintenant(),
        fin = fin_de_piste(textes[nom]),
    }
    if DIAG then log("cinematique detectee : " .. nom) end
end

local function arreter(raison)
    if courant and DIAG then log("fin de " .. courant.nom .. " (" .. raison .. ")") end
    courant = nil
end

local function joue(composant)
    local ok, res = pcall(function() return composant:IsPlaying() end)
    return ok and res == true
end

-- Avance le chrono de la piste en cours. Le temps ne court que pendant la
-- lecture : mettre le jeu en pause suspend le son, donc les sous-titres, et
-- couper la scene (skip) arrete le son, donc les efface.
local function suivre()
    local c = courant.composant
    if not c or not c:IsValid() then return arreter("composant disparu") end

    local etat = etat_lecture(c)
    local instant = maintenant()

    if etat == 1 then return arreter("son arrete") end          -- Stopped
    if etat == nil and not joue(c) then
        return arreter("le son ne joue plus")
    end

    if etat ~= 2 then                                            -- pas en pause
        courant.ecoule = courant.ecoule + (instant - courant.dernier)
    end
    courant.dernier = instant

    -- Une piste se termine quand son texte est epuise, sans attendre que le
    -- composant se taise : en jeu, MS_SimonA s'est declare « en train de
    -- jouer » pendant 37 secondes pour un son d'une seconde, ce qui masquait
    -- toutes les voix suivantes.
    if courant.ecoule > courant.fin + 1.0 then
        arreter("texte epuise")
    end
end

-- Candidats : les AudioComponent que le moteur vient de creer. On les surveille
-- quelques secondes, le temps que leur son soit assigne et lance.
--
-- Balayer tous les AudioComponent du jeu toutes les 100 ms a fait tomber le
-- jeu (violation d'acces, lecture de 0x53) : pendant les transitions de scene,
-- un composant meurt entre deux appels, et le IsValid d'UE4SS ne filtre pas
-- les objets en attente de destruction. Ici on n'interroge qu'une poignee
-- d'objets frais au lieu de plusieurs dizaines a chaque tour.
local candidats = {}         -- son pas encore identifie, surveille brievement
local voix = {}              -- composants porteurs d'une piste, gardes a vue
local SURVEILLANCE = 8       -- secondes avant d'abandonner un candidat muet
local inventorier            -- defini plus bas, avec le reste du diagnostic

-- Le nom du son est lu des la creation, sans attendre que ca joue : le
-- composant de la voix de Wade appartient a BP_WadeCinema, il nait au
-- chargement du motel et ne demarre que deux minutes plus tard. Le chercher
-- parmi les composants « en train de jouer » le manquait a tous les coups.
local function examiner(c)
    local nom = nom_du_son(c)
    if not nom then return false end       -- son pas encore assigne
    inventorier(nom)
    if textes[nom] then
        voix[#voix + 1] = { objet = c, nom = nom }
        if DIAG then log("voix reperee : " .. nom .. " (en attente)") end
    end
    return true
end

NotifyOnNewObject("/Script/Engine.AudioComponent", function(objet)
    if not examiner(objet) then
        candidats[#candidats + 1] = { objet = objet, fin = maintenant() + SURVEILLANCE }
    end
end)

local function sonder()
    if courant then suivre() end

    -- Les composants de voix connus. On guette le *depart* d'un son — le
    -- passage de silencieux a jouant — et non le simple fait qu'il joue : un
    -- composant se declare en lecture bien apres la fin de sa replique, et
    -- prendre ca pour un depart rearmait sans cesse la meme piste.
    --
    -- La liste est parcourue jusqu'au bout AVANT de demarrer quoi que ce soit.
    -- Sortir de la boucle des le premier son qui joue tronquait la liste des
    -- survivants a ce qu'on avait deja vu : la premiere voix jouee effacait
    -- toutes les autres, definitivement.
    local vivantes, depart = {}, nil
    for _, v in ipairs(voix) do
        local c = v.objet
        if c and c:IsValid() then
            vivantes[#vivantes + 1] = v
            local en_lecture = joue(c)
            if en_lecture and not v.jouait and not depart then depart = v end
            v.jouait = en_lecture
        end
    end
    voix = vivantes

    -- Un depart l'emporte sur la piste en cours : deux repliques peuvent se
    -- suivre de pres, la plus recente est celle qu'on entend.
    if depart then
        demarrer(depart.nom, depart.objet)
        return
    end
    if courant then return end

    -- Les nouveaux venus dont le son n'etait pas encore assigne.
    if #candidats == 0 then return end
    local instant = maintenant()
    local restants = {}
    for _, cand in ipairs(candidats) do
        local c = cand.objet
        if c and c:IsValid() and not examiner(c) and instant < cand.fin then
            restants[#restants + 1] = cand
        end
    end
    candidats = restants
end

-- ------------------------------------------------------------------ affichage

local function replique_courante()
    if maintenant() < essai_jusqua then
        return "Essai de rendu — accents : éàçùôî. Ligne longue pour verifier"
            .. " la coupe automatique du texte sur la largeur de l'ecran."
    end
    if not courant then return nil end
    local t = courant.ecoule
    for _, r in ipairs(courant.repliques) do
        if t >= r.debut and t <= r.fin then return r.texte end
    end
    return nil
end

local function resoudre_police()
    if police and police:IsValid() then return police end
    for _, chemin in ipairs({
        "/Game/Fonts/Outfit-Bold_Font.Outfit-Bold_Font",
        "/Game/Fonts/SourceCodePro-Regular_Font.SourceCodePro-Regular_Font",
        "/Engine/EngineFonts/Roboto.Roboto",
    }) do
        local f = StaticFindObject(chemin)
        if f and f:IsValid() then
            police = f
            if DIAG then log("police : " .. chemin) end
            return police
        end
    end
    return nil
end

-- La coupe des lignes et le centrage sont laisses a UMG (SetAutoWrapText,
-- SetJustification) : inutile de compter les caracteres a la main.
--
-- Le widget est bati piece par piece : UserWidget nu, arbre de widgets, toile,
-- bloc de texte. Le jeu ne fournit aucun WidgetBlueprint de sous-titre a
-- reutiliser, et sa classe UserWidget nue n'a pas d'arbre — on le pose donc.
local vue = nil          -- { widget, bloc, toile }
local etape = "aucune"   -- derniere etape atteinte, pour lire les echecs

-- ESlateVisibility : 0 Visible, 1 Collapsed, 2 Hidden,
-- 3 HitTestInvisible (dessine, clics traversent soi + enfants),
-- 4 SelfHitTestInvisible (clics traversent soi, PAS les enfants).
--
-- Le TextBlock est Visible par defaut. Avec seulement SelfHitTestInvisible
-- sur le UserWidget, la bande basse (Y=0.88, 100 px) avalait les clics —
-- champ CryptChat injoignable apres l'intro Wade, overlay jamais retire.
local VIS_COLLAPSE = 1
local VIS_CLICKTHROUGH = 3

local function pas_de_focus(w)
    if not w then return end
    pcall(function() w:SetIsFocusable(false) end)
    pcall(function() w.bIsFocusable = false end)
end

local function clic_traverse(w)
    if not w then return end
    pcall(function() w:SetVisibility(VIS_CLICKTHROUGH) end)
    pas_de_focus(w)
end

local function replier(w)
    if not w then return end
    pcall(function() w:SetVisibility(VIS_COLLAPSE) end)
end

local function appliquer_overlay(montre)
    if not vue then return end
    if montre then
        clic_traverse(vue.widget)
        clic_traverse(vue.toile)
        clic_traverse(vue.bloc)
    else
        replier(vue.widget)
        replier(vue.bloc)
        clic_traverse(vue.toile)
    end
end

local function classe(chemin)
    local c = StaticFindObject(chemin)
    if not c or not c:IsValid() then
        error("introuvable : " .. chemin, 0)
    end
    return c
end

local function construire()
    etape = "PlayerController"
    local pc = FindFirstOf("PlayerController")
    if not pc or not pc:IsValid() then
        -- Arrive au menu ou pendant un chargement : sans interet en usage
        -- normal, la construction sera retentee au tour suivant.
        if DIAG then log("pas de PlayerController : widget non construit") end
        return nil
    end

    etape = "Create"
    local lib = classe("/Script/UMG.Default__WidgetBlueprintLibrary")
    local widget = lib:Create(pc, classe("/Script/UMG.UserWidget"), pc)
    if not widget or not widget:IsValid() then return nil end

    etape = "WidgetTree"
    local arbre = StaticConstructObject(classe("/Script/UMG.WidgetTree"), widget)
    widget.WidgetTree = arbre

    etape = "CanvasPanel"
    local toile = StaticConstructObject(classe("/Script/UMG.CanvasPanel"), arbre)
    arbre.RootWidget = toile

    etape = "TextBlock"
    local bloc = StaticConstructObject(classe("/Script/UMG.TextBlock"), arbre)

    etape = "AddChildToCanvas"
    local place = toile:AddChildToCanvas(bloc)

    -- Bande ancree au bas de l'ecran, sur 80 % de la largeur : la position
    -- suit la resolution sans qu'on ait a mesurer quoi que ce soit.
    -- Ancre : une ligne horizontale a 88 % de la hauteur, large de 80 %.
    -- Le texte se dessine en haut de son bloc, donc cette ligne est celle de
    -- la PREMIERE ligne de sous-titre ; une seconde ligne descend en dessous
    -- et reste largement dans l'ecran. Avec une ancre etiree en X et
    -- ponctuelle en Y, Bottom donne la hauteur du bloc, pas une marge.
    etape = "ancrage"
    place:SetAnchors({ Minimum = { X = 0.1, Y = 0.88 },
                       Maximum = { X = 0.9, Y = 0.88 } })
    place:SetOffsets({ Left = 0, Top = 0, Right = 0, Bottom = 100 })
    place:SetAlignment({ X = 0, Y = 0 })
    place:SetAutoSize(false)        -- autosize couperait le retour a la ligne
    place:SetZOrder(1000)

    etape = "mise en forme"
    pcall(function() bloc:SetJustification(1) end)          -- centre
    pcall(function() bloc:SetAutoWrapText(true) end)
    pcall(function() bloc:SetShadowOffset({ X = 2, Y = 2 }) end)
    pcall(function()
        bloc:SetShadowColorAndOpacity({ R = 0, G = 0, B = 0, A = 0.9 })
    end)
    local p = resoudre_police()
    if p then
        local pose = pcall(function()
            bloc:SetFont({ FontObject = p, Size = 26 })
        end)
        if not pose then
            pcall(function()
                bloc.Font.FontObject = p
                bloc.Font.Size = 26
            end)
        end
    end

    etape = "AddToViewport"
    widget:AddToViewport(1000)
    clic_traverse(widget)
    clic_traverse(toile)
    clic_traverse(bloc)

    etape = "pret"
    if DIAG then log("widget construit : " .. widget:GetFullName()) end
    return { widget = widget, bloc = bloc, toile = toile }
end

local function vue_valide()
    if not vue then return false end
    local ok, res = pcall(function()
        return vue.widget:IsValid() and vue.bloc:IsValid()
               and vue.toile:IsValid() and vue.widget:IsInViewport()
    end)
    return ok and res == true
end

-- SetText attend un FText, jamais une chaine Lua : passer la chaine laisse le
-- parametre non initialise et le jeu tombe sur une violation d'acces (lecture
-- de 0x70) que pcall ne peut pas rattraper — c'est un plantage natif, pas une
-- erreur Lua. On construit donc toujours un vrai FText avant l'appel.
local voie_texte = nil

local function fabriquer_texte(texte)
    if type(FText) == "function" then
        local ok, res = pcall(FText, texte)
        if ok and res then
            if not voie_texte then
                voie_texte = "FText()"
                if DIAG then log("texte via " .. voie_texte) end
            end
            return res
        end
    end
    local lib = StaticFindObject("/Script/Engine.Default__KismetTextLibrary")
    if lib and lib:IsValid() then
        local ok, res = pcall(function() return lib:Conv_StringToText(texte) end)
        if ok and res then
            if not voie_texte then
                voie_texte = "Conv_StringToText"
                if DIAG then log("texte via " .. voie_texte) end
            end
            return res
        end
    end
    return nil
end

local function poser_texte(bloc, texte)
    local ftexte = fabriquer_texte(texte)
    if not ftexte then
        log("aucun moyen de construire un FText — texte non affiche")
        return false
    end
    return pcall(function() bloc:SetText(ftexte) end)
end

local dernier_texte = nil

local function rafraichir()
    local texte = replique_courante()
    if texte == dernier_texte and vue_valide() then return end

    if not vue_valide() then
        if not texte then return end          -- rien a montrer, rien a batir
        vue = nil
        local ok, res = pcall(construire)
        if not ok then
            log("echec de construction a l'etape " .. etape .. " : " .. tostring(res))
            return
        end
        vue = res
        if not vue then return end
        dernier_texte = nil
    end

    dernier_texte = texte
    if not poser_texte(vue.bloc, texte or "") then
        log("SetText refuse (etape " .. etape .. ")")
    end
    appliquer_overlay(texte ~= nil and texte ~= "")
end

-- ---------------------------------------------------------------- branchement

charger()

-- Tout le travail se fait sur le fil du jeu, sondage compris. La premiere
-- version appelait FindAllOf et IsPlaying depuis le fil d'UE4SS : le moteur
-- detruisait un AudioComponent entre les deux et le jeu tombait sur une
-- violation d'acces (lecture de 0x70), pile dans les frames Lua.
LoopAsync(INTERVALLE, function()
    tic = tic + (INTERVALLE / 1000)
    ExecuteInGameThread(function()
        local ok, err = pcall(sonder)
        if not ok then log("erreur de sondage : " .. tostring(err)) end
        local ok2, err2 = pcall(rafraichir)
        if not ok2 then log("erreur d'affichage : " .. tostring(err2)) end
    end)
    return false
end)

-- F9 affiche une ligne d'essai pendant dix secondes : de quoi verifier le
-- rendu n'importe ou dans le jeu, sans jouer jusqu'a une cinematique.
RegisterKeyBind(Key.F9, function()
    essai_jusqua = maintenant() + 10
    if DIAG then log("ligne d'essai demandee (10 s)") end
end)

-- Inventaire : aucune cinematique n'a ete detectee au premier essai. On nomme
-- donc tout son qui joue, une fois par nom, pour savoir si les voix passent
-- vraiment par un AudioComponent et sous quel nom elles y apparaissent.
local vus = {}
local vus_n = 0

-- L'inventaire ne parle plus que des candidats — les composants tout juste
-- crees, deja inspectes par le sondage. Sa version precedente rebalayait tous
-- les AudioComponent du jeu et leur demandait leur classe : c'est ce trafic
-- qui a fait tomber le jeu.
inventorier = function(nom)
    if not DIAG or vus[nom] or vus_n >= 40 then return end
    vus[nom] = true
    vus_n = vus_n + 1
    log("inventaire : joue « " .. nom .. " »")
end

-- Veille : dit une fois par minute si le widget tient, et sinon a quelle
-- etape la construction s'arrete.
LoopAsync(20000, function()
    if not DIAG then return true end
    diag_tour = diag_tour + 1
    if diag_tour > 12 then return true end
    log("veille " .. diag_tour .. " : widget "
        .. (vue_valide() and "en place" or "absent") .. ", etape " .. etape
        .. ", sons vus " .. vus_n)
    return false
end)

log("mod pret (dossier " .. RACINE .. ") — F9 pour une ligne d'essai")
