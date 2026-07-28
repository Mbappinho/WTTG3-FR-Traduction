; WTTG3 FR — menu mini-jeux AZERTY (AutoHotkey v2)
; Attribution : logique inspiree du mod communautaire "WTTG3 AZERTY Rebind"
; (detection UE4SS + swap AHK pendant NativeOnKeyDown des hacks).
;
; Le pak FR_AZERTY_P gere deja Enhanced Input (ZQSD).
; Ici : echange clavier UNIQUEMENT pendant les mini-jeux directionnels.

#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent
A_IconTip := "WTTG3 AZERTY mini-jeux"

KEY_DIR := A_ScriptDir "\WTTGSD\Binaries\Win64\ue4ss\Mods\AzertyRemap\"
MENU_INI := A_ScriptDir "\WTTG3-Menu.ini"
FLAG_FILE := KEY_DIR "minigame.flag"

; Touches physiques AZERTY par defaut (cible UE -> touche joueur)
AzertyPhys := Map("W", "Z", "A", "Q", "S", "S", "D", "D", "SpaceBar", "SpaceBar")

MgTargets := Map("W","w", "A","a", "S","s", "D","d",
                 "SpaceBar","Space",
                 "Up","Up", "Down","Down", "Left","Left", "Right","Right")

MgAhkName(ueName) {
    if (StrLen(ueName) = 1)
        return StrLower(ueName)
    if (ueName = "SpaceBar")
        return "Space"
    if (ueName = "Up" || ueName = "Down" || ueName = "Left" || ueName = "Right")
        return ueName
    return ""
}

MgKeyRows := [
    { target: "W",        label: "Haut / Forward" },
    { target: "A",        label: "Gauche / Left" },
    { target: "S",        label: "Bas / Back" },
    { target: "D",        label: "Droite / Right" },
    { target: "SpaceBar", label: "Action / Space" }
]

; Defauts : MemDealloc + ShiftSEQ ON (directions). StackPusher / TOKENINE = souris (OFF).
; Kernal OFF (saisie texte). Swap + focus clic auto au demarrage du decompte.
MgGames := [
    { type: "1", name: "memDEALLOCATER", def: true },
    { type: "2", name: "stackPUSHER",    def: false },
    { type: "3", name: "K3RN3LC0MP1L3R", def: false },
    { type: "4", name: "TOKENINE",       def: false },
    { type: "5", name: "shiftSEQ",       def: true }
]
MgSwapTypes := Map()
MgKeyCfg := Map()
swapOn := false
SwapKeys := Map()
regKeys := Map()

MgLoadConfig() {
    global MgGames, MgSwapTypes, MENU_INI
    MgSwapTypes := Map()
    for gme in MgGames {
        v := IniRead(MENU_INI, "Minigames", gme.type, gme.def ? "1" : "0")
        if (v = "1")
            MgSwapTypes[gme.type] := true
    }
}
MgSaveConfig() {
    global MgGames, MgSwapTypes, MENU_INI
    for gme in MgGames
        try IniWrite(MgSwapTypes.Has(gme.type) ? "1" : "0", MENU_INI, "Minigames", gme.type)
}

MgPhysFor(target) {
    global MgKeyCfg, AzertyPhys
    if MgKeyCfg.Has(target)
        return MgKeyCfg[target]
    if AzertyPhys.Has(target)
        return AzertyPhys[target]
    return target
}

MgBuildSwap() {
    global SwapKeys, MgTargets, MgKeyRows
    m := Map()
    for r in MgKeyRows {
        phys := MgPhysFor(r.target)
        if (phys = r.target)
            continue
        src := MgAhkName(phys)
        if (src != "" && MgTargets.Has(r.target))
            m[src] := MgTargets[r.target]
    }
    SwapKeys := m
    return m
}

MinigameDown(key, *) {
    global SwapKeys
    if SwapKeys.Has(key)
        Send("{Blind}{" SwapKeys[key] " down}")
}
MinigameUp(key, *) {
    global SwapKeys
    if SwapKeys.Has(key)
        Send("{Blind}{" SwapKeys[key] " up}")
}

MgUnregister() {
    global regKeys
    for k, v in regKeys {
        try Hotkey("*" k, "Off")
        try Hotkey("*" k " up", "Off")
    }
}

GAME_EXE := "WTTGSD-Win64-Shipping.exe"

; Les hacks lisent NativeOnKeyDown : sans focus Slate sur le widget,
; Z/Q ne font rien tant que le joueur n'a pas fait un clic gauche.
; On reproduit ce clic au centre de la fenetre (curseur restaure apres).
FocusGameForMinigame(*) {
    global GAME_EXE
    win := "ahk_exe " GAME_EXE
    if !WinExist(win)
        return
    try {
        WinActivate(win)
        if !WinWaitActive(win, , 0.4)
            return
        CoordMode("Mouse", "Screen")
        MouseGetPos(&mx, &my)
        WinGetClientPos(&cx, &cy, &cw, &ch, win)
        if (cw < 50 || ch < 50)
            return
        ; Centre client : zone neutre pendant le decompte 3-2-1
        Click(cx + (cw // 2), cy + (ch // 2))
        MouseMove(mx, my, 0)
    } catch {
    }
}

SetSwap(on) {
    global swapOn, SwapKeys, regKeys
    if (on = swapOn)
        return
    if (on) {
        MgUnregister()
        MgBuildSwap()
        regKeys := Map()
        for k, v in SwapKeys {
            try {
                Hotkey("*" k, MinigameDown.Bind(k), "On")
                Hotkey("*" k " up", MinigameUp.Bind(k), "On")
                regKeys[k] := v
            }
        }
        ; Pas de TrayTip ici : ca vole le focus et force un reclic.
        ; Clic auto apres un court delai (widget countdown pret).
        SetTimer(FocusGameForMinigame, -250)
    } else {
        MgUnregister()
    }
    swapOn := on
}

; ---------- GUI ----------
g := Gui("+AlwaysOnTop -MinimizeBox", "WTTG3 FR — AZERTY mini-jeux")
g.Add("Text", "w420", "Swap AZERTY auto : MemDealloc + ShiftSEQ (focus clic inclus).`n"
    . "StackPusher / TOKENINE = souris (OFF). KernalCompiler = saisie (OFF).`n"
    . "F1 = activer/desactiver un jeu. Enhanced Input = pak FR_AZERTY_P.")
cbs := Map()
MgLoadConfig()
for gme in MgGames {
    cb := g.Add("Checkbox", "w420", gme.name " (opt-out si decoche)")
    cb.Value := MgSwapTypes.Has(gme.type) ? 1 : 0
    cb.OnEvent("Click", MgToggle.Bind(gme.type))
    cbs[gme.type] := cb
}
g.Add("Text", "w420 cGray", "F1 = ce menu. Se ferme avec le jeu.")
g.OnEvent("Close", (*) => g.Hide())

MgToggle(gameType, ctrl, *) {
    global MgSwapTypes
    if (ctrl.Value)
        MgSwapTypes[gameType] := true
    else if MgSwapTypes.Has(gameType)
        MgSwapTypes.Delete(gameType)
    MgSaveConfig()
}

ToggleGui(*) {
    global g
    if WinExist("ahk_id " g.Hwnd) && DllCall("IsWindowVisible", "ptr", g.Hwnd)
        g.Hide()
    else
        g.Show()
}
F1:: ToggleGui()

; ---------- Watch minigame.flag ----------
; Auto : tout mini-jeu detecte active le swap, sauf KernalCompiler (3 = saisie).
; Les cases F1 servent seulement d'opt-out (decocher = pas de swap pour ce type).
lastFlag := ""
WatchFlag() {
    global FLAG_FILE, lastFlag, MgSwapTypes
    try {
        if !FileExist(FLAG_FILE) {
            SetSwap(false)
            lastFlag := ""
            return
        }
        raw := Trim(FileRead(FLAG_FILE))
        if (raw = lastFlag)
            return
        lastFlag := raw
        if (raw = "" || raw = "0") {
            SetSwap(false)
            return
        }
        ; Auto ON pour MemDealloc (1) + ShiftSEQ (5). StackPusher/TOKENINE/Kernal OFF par defaut.
        ; Decoche/coche F1 = opt-in/opt-out.
        if (raw = "3") {
            SetSwap(false)
            return
        }
        if MgSwapTypes.Has(raw)
            SetSwap(true)
        else
            SetSwap(false)
    } catch {
    }
}
SetTimer(WatchFlag, 200)

; Exit when game closes (shipping exe)
WatchGame() {
    global GAME_EXE
    if !ProcessExist(GAME_EXE) {
        SetSwap(false)
        ExitApp()
    }
}
SetTimer(WatchGame, 2000)

MgLoadConfig()
return
