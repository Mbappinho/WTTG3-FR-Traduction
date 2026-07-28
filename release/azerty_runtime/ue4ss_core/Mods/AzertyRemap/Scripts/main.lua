-- ============================================================
--  AzertyRemap : configurable key rebinding for WTTG3
--
--  - remap.ini : per-key or per-action rules
--  - actions_dump.txt : every game action + keys (generated)
--  - F10 in game : hot-reload remap.ini
--  - Graphical config : WTTG3-KeyMenu.exe (game root folder, F9)
--
--  Original keys are kept in memory: every config application
--  starts from the originals (idempotent).
-- ============================================================

local function Log(msg)
    print("[AzertyRemap] " .. msg .. "\n")
end

-- ---------- Mod folder ----------
local BASE = nil
do
    local candidates = {
        "ue4ss\\Mods\\AzertyRemap\\",
        "WTTGSD\\Binaries\\Win64\\ue4ss\\Mods\\AzertyRemap\\",
    }
    for _, p in ipairs(candidates) do
        local f = io.open(p .. "Scripts\\main.lua", "r")
        if f then f:close(); BASE = p; break end
    end
    if not BASE then BASE = candidates[1] end
end

-- ---------- Config ----------
local keyRules = {}     -- ["W"] = "Z"          (everywhere)
local actionRules = {}  -- ["IA_Move|W"] = "Z"  (specific action)

local function LoadConfig()
    keyRules, actionRules = {}, {}
    local f = io.open(BASE .. "remap.ini", "r")
    if not f then
        Log("remap.ini not found (" .. BASE .. ") - no rules applied")
        return
    end
    local section = ""
    for line in f:lines() do
        line = line:gsub("^%s+", ""):gsub("%s+$", "")
        if line ~= "" and not line:match("^[;#]") then
            local sec = line:match("^%[(.+)%]$")
            if sec then
                section = sec:lower()
            else
                local lhs, rhs = line:match("^(.-)%s*=%s*(.+)$")
                if lhs and rhs then
                    if section == "actions" then
                        local action, key = lhs:match("^(.-)%s*:%s*(.+)$")
                        if action and key then
                            actionRules[action .. "|" .. key] = rhs
                        end
                    else
                        keyRules[lhs] = rhs
                    end
                end
            end
        end
    end
    f:close()
    local nk, na = 0, 0
    for _ in pairs(keyRules) do nk = nk + 1 end
    for _ in pairs(actionRules) do na = na + 1 end
    Log(string.format("Config loaded: %d key rule(s), %d action rule(s)", nk, na))
end

-- ---------- State ----------
local originals = {}   -- addr -> { [index] = original keyName }
local knownIMCs = {}   -- addr -> IMC object
local entries = {}     -- array of {action, orig, imc}
local entryKeys = {}   -- dedupe set

local function EffectiveKey(action, orig)
    return actionRules[action .. "|" .. orig] or keyRules[orig] or orig
end

-- Relit le dump existant pour ne JAMAIS perdre une action deja vue.
-- Sans ca, la liste repart de zero a chaque lancement du jeu et le
-- fichier est reecrit avec le peu qui est charge sur le moment : les
-- actions des mini-jeux (ShiftSeq, MemDealloc), chargees seulement
-- pendant le mini-jeu, disparaissaient au scan suivant.
local function LoadExistingDump()
    local f = io.open(BASE .. "actions_dump.txt", "r")
    if not f then return end
    for line in f:lines() do
        local action, orig, imc = line:match("^(%S+)%s+(%S+)%s+%->%s+%S+%s+%(IMC:%s*(.-)%)%s*$")
        if action and orig then
            local k = action .. "|" .. orig
            if not entryKeys[k] then
                entryKeys[k] = true
                table.insert(entries, { action = action, orig = orig, imc = imc or "?" })
            end
        end
    end
    f:close()
end

local function WriteDump()
    local f = io.open(BASE .. "actions_dump.txt", "w")
    if not f then return end
    f:write("Game actions detected (original key -> current key)\n")
    f:write("Rebind in remap.ini, [Actions] section:  ActionName:OriginalKey=NewKey\n")
    f:write(string.rep("=", 70) .. "\n")
    local lines = {}
    for _, e in ipairs(entries) do
        table.insert(lines, string.format("%-40s %-12s -> %s  (IMC: %s)",
            e.action, e.orig, EffectiveKey(e.action, e.orig), e.imc))
    end
    table.sort(lines)
    for _, l in ipairs(lines) do f:write(l .. "\n") end
    f:close()
end

local function PatchIMC(IMC)
    if not IMC or not IMC:IsValid() then return end
    local addr = IMC:GetAddress()

    local ok, err = pcall(function()
        local mappings = IMC.Mappings
        if mappings:GetArrayNum() == 0 then return end
        local imcName = IMC:GetFName():ToString()

        if not originals[addr] then
            originals[addr] = {}
            mappings:ForEach(function(index, elem)
                originals[addr][index] = elem:get().Key.KeyName:ToString()
            end)
        end
        knownIMCs[addr] = IMC

        mappings:ForEach(function(index, elem)
            local m = elem:get()
            local origKey = originals[addr][index]
            if origKey then
                local actionName = "?"
                pcall(function() actionName = m.Action:GetFName():ToString() end)

                local target = EffectiveKey(actionName, origKey)
                if m.Key.KeyName:ToString() ~= target then
                    m.Key.KeyName = FName(target)
                    Log(string.format("%s / %s : %s -> %s", imcName, actionName, origKey, target))
                end

                local ek = actionName .. "|" .. origKey
                if not entryKeys[ek] then
                    entryKeys[ek] = true
                    table.insert(entries, {action = actionName, orig = origKey, imc = imcName})
                end
            end
        end)
    end)

    if not ok then
        Log("Error: " .. tostring(err))
    end
end

local function RequestRebuild()
    pcall(function()
        local subsys = FindFirstOf("EnhancedInputLocalPlayerSubsystem")
        if subsys and subsys:IsValid() then
            subsys:RequestRebuildControlMappings({}, 1)
        end
    end)
end

local function PatchAllLoaded()
    local all = FindAllOf("InputMappingContext")
    if all then
        for _, imc in ipairs(all) do PatchIMC(imc) end
    end
    RequestRebuild()
    WriteDump()
end

local function ReapplyAll()
    for addr, imc in pairs(knownIMCs) do
        if not imc:IsValid() then
            knownIMCs[addr] = nil
            originals[addr] = nil
        end
    end
    PatchAllLoaded()
end

-- ---------- Startup ----------
LoadConfig()
LoadExistingDump()   -- conserve les actions vues lors des sessions precedentes

ExecuteInGameThread(function()
    PatchAllLoaded()
end)

NotifyOnNewObject("/Script/EnhancedInput.InputMappingContext", function(imc)
    ExecuteWithDelay(500, function()
        ExecuteInGameThread(function()
            PatchIMC(imc)
            RequestRebuild()
            WriteDump()
        end)
    end)
end)

RegisterInitGameStatePostHook(function()
    ExecuteWithDelay(1000, function()
        ExecuteInGameThread(function()
            PatchAllLoaded()
        end)
    end)
end)

-- F10 : hot reload of remap.ini (used by the overlay and hand edits)
pcall(function()
    RegisterKeyBind(Key.F10, function()
        ExecuteInGameThread(function()
            LoadConfig()
            ReapplyAll()
            Log("Config reloaded from remap.ini")
        end)
    end)
end)

-- Auto-start AHK overlay (game root). Needs AutoHotkey64.exe + script next to the game exe folder root.
-- CWD when UE4SS runs is typically WTTGSD\Binaries\Win64.
-- Relance a chaque load UE4SS ; #SingleInstance Force cote AHK evite les doublons.
pcall(function()
    local candidates = {
        { ahk = "..\\..\\..\\AutoHotkey64.exe", script = "..\\..\\..\\WTTG3-Menu-Touches.ahk" },
        { ahk = "AutoHotkey64.exe", script = "WTTG3-Menu-Touches.ahk" },
    }
    for _, c in ipairs(candidates) do
        local f = io.open(c.script, "r")
        if f then
            f:close()
            local ahkOk = io.open(c.ahk, "r")
            if ahkOk then
                ahkOk:close()
                -- cmd /c start : non-bloquant, chemins relatifs OK depuis CWD Win64
                os.execute('cmd /c start "" /min "' .. c.ahk .. '" "' .. c.script .. '"')
                Log("Overlay auto-started: " .. c.script)
            else
                os.execute('cmd /c start "" /min "' .. c.script .. '"')
                Log("Overlay auto-started via association: " .. c.script)
            end
            break
        end
    end
end)

-- ------------------------------------------------------------
--  Detection des mini-jeux de hack
--
--  Les 5 mini-jeux (shiftSEQ, memDEALLOC, stackPUSHER, TOKENINE,
--  kernalCOMPILER) lisent le clavier en C++ NATIF, via la virtuelle
--  Slate NativeOnKeyDown. Prouve par le dump CXXHeaderGenerator :
--  aucune UFunction du module ne prend un FKey, et les classes de
--  mini-jeu n'exposent aucun OnKeyDown. Le remap Enhanced Input ne
--  peut donc PAS les atteindre, quoi qu'on fasse cote moteur.
--
--  On se contente ici de SIGNALER qu'un mini-jeu tourne, en ecrivant
--  minigame.flag. C'est WTTG3-Menu.ahk qui echange les touches au
--  niveau clavier pendant ce temps, puis remet tout en place.
--
--  TROUVER CE SIGNAL A DEMANDE SIX SONDES. Ce qui NE marche pas :
--    existence des widgets  10 instances vivantes en permanence
--                           (2 par jeu) -- ne distingue rien
--    IsVisible/IsInViewport constants
--    IsRendered             vrai en permanence sur 5 instances,
--                           y compris les jeux jamais lances
--    focus clavier          kb/any/desc a 0 MEME en pleine partie
--    CurrentTier            ne se vide jamais apres la partie :
--                           drapeau bloque a 1, ZQSD casse en jeu
--                           normal (le bug du 20/07)
--    VMBrowser:HackMachine  jusqu'a 3 minutes d'avance sur le debut
--    VMBrowser:HackCompleted se declenche ~14 s APRES le debut, en
--                           pleine partie -- piege absolu comme fin
--
--  CE QUI MARCHE :
--    DEBUT = TB_CountDown passe de vide a non-vide. C'est le
--            decompte 3-2-1 de lancement, porte par UHackMiniGame
--            donc commun aux 5 jeux. Verifie sur ShiftSeq ET
--            MemDealloc ("" -> 3 -> 2 -> 1 -> "").
--    FIN   = ComputerSubsystem:PlayerFinishedHackMiniGame.
--            Verifie sur partie gagnee ET sur chrono expire, y
--            compris sur MemDealloc qui n'a pas de TimesUpForGame.
-- ------------------------------------------------------------

-- EHackGames
local GAMES = { [1]="MemDealloc", [2]="StackPusher", [3]="KernalCompiler",
                [4]="TOKENINE",   [5]="ShiftSeq" }

local activeGame = nil      -- type de mini-jeu en cours, ou nil
local startedAt  = 0
local lastCD     = {}       -- adresse -> dernier texte du decompte

local function WriteMinigameFlag()
    local f = io.open(BASE .. "minigame.flag", "w")
    if not f then return end
    f:write(activeGame and tostring(activeGame) or "0")
    f:close()
end

-- Focus clavier Slate sur le widget hack (independant de ou regarde la camera).
-- Le clic AHK au centre ecran ne marche que si l'UI hack est sous le centre ;
-- si le joueur regarde ailleurs dans le motel, SetKeyboardFocus reste la bonne cible.
local function TryFocusMinigameWidget(o)
    if not o then return end
    local okv, valid = pcall(function() return o:IsValid() end)
    if not (okv and valid) then return end
    pcall(function() o:SetKeyboardFocus() end)
    pcall(function()
        local pc = o:GetOwningPlayer()
        if pc then o:SetUserFocus(pc) end
    end)
    pcall(function() o:SetFocus() end)
end

local function MinigameOn(gt, widget)
    if activeGame == gt then return end
    activeGame = gt
    startedAt = os.clock()
    WriteMinigameFlag()
    TryFocusMinigameWidget(widget)
    -- Retry : Slate pas toujours pret au frame du decompte
    pcall(function()
        ExecuteWithDelay(300, function()
            ExecuteInGameThread(function()
                TryFocusMinigameWidget(widget)
            end)
        end)
    end)
    Log("Hack minigame started (" .. (GAMES[gt] or "?") .. ") -> keyboard swap ON")
end

local function MinigameOff(why)
    if activeGame == nil then return end
    activeGame = nil
    WriteMinigameFlag()
    Log("Hack minigame ended (" .. why .. ") -> keyboard swap OFF")
end

-- Seules 5 des 10 instances exposent un TB_CountDown lisible.
local function ReadCountDown(o)
    local v = nil
    pcall(function() v = o.TB_CountDown:GetText():ToString() end)
    if v == nil then pcall(function() v = o.TB_CountDown.Text:ToString() end) end
    return v
end

local function MinigameWatch()
    pcall(function()
        ExecuteInGameThread(function()
            local ok, all = pcall(FindAllOf, "HackMiniGame")
            if ok and all then
                for _, o in ipairs(all) do
                    local okv, valid = pcall(function() return o:IsValid() end)
                    if okv and valid then
                        local n = "?"
                        pcall(function() n = o:GetFName():ToString() end)
                        if not n:find("^Default__") then
                            local cd = ReadCountDown(o)
                            if cd ~= nil then
                                local addr = 0
                                pcall(function() addr = o:GetAddress() end)
                                if lastCD[addr] == "" and cd ~= "" then
                                    local gt = -1
                                    pcall(function()
                                        gt = math.floor(tonumber(tostring(o.MyGameType)) or -1)
                                    end)
                                    MinigameOn(gt, o)
                                end
                                lastCD[addr] = cd
                            end
                        end
                    end
                end
            end

            -- Filet : aucun mini-jeu ne dure 15 minutes. Si le drapeau
            -- tient plus longtemps, c'est qu'une fin nous a echappe.
            -- On relache : mieux vaut perdre l'echange que bloquer ZQSD.
            if activeGame and (os.clock() - startedAt) > 900 then
                MinigameOff("safety timeout")
            end
        end)
    end)
    pcall(function() ExecuteWithDelay(300, MinigameWatch) end)
end

pcall(function()
    RegisterHook("/Script/WTTGSD.ComputerSubsystem:PlayerFinishedHackMiniGame", function()
        MinigameOff("game finished")
    end)
end)

-- Filet supplementaire pour les 3 classes qui l'exposent. MemDealloc
-- et KernalCompiler n'ont pas cette fonction, mais le test du 21/07
-- montre que PlayerFinishedHackMiniGame part quand meme sur chrono
-- expire -- ceci n'est qu'une ceinture de plus.
for _, cls in ipairs({ "ShiftSEQ", "StackPusher", "TOKENINE" }) do
    pcall(function()
        RegisterHook("/Script/WTTGSD." .. cls .. ":TimesUpForGame", function()
            MinigameOff("time up")
        end)
    end)
end

WriteMinigameFlag()               -- etat propre au demarrage
pcall(function() ExecuteWithDelay(5000, MinigameWatch) end)

Log("Mod loaded (folder: " .. BASE .. ")")
