-- Signature de StaticConstructObject_Internal pour Welcome to the Game III.
--
-- UE4SS resout huit reperes sur neuf dans ce binaire (EngineVersion 5.6,
-- GUObjectArray, GMalloc, FName::ToString, GNatives...) mais echoue sur
-- StaticConstructObject_Internal, et abandonne apres 59 tentatives :
--   Fatal Error: PS scan timed out
--
-- Le prologue ci-dessous est celui des jeux UE5 recents (configs UE4SS de
-- Whiskerwood et Tokyo Xtreme Racer, identiques). Verifie contre
-- WTTGSD-Win64-Shipping.exe : une seule correspondance, au decalage fichier
-- 0x15e57a0 — la variante a jokers de Deadly Days Roadtrip tombe au meme
-- endroit, ce qui confirme la cible.
--
-- A revalider apres chaque mise a jour Steam : le decalage bougera, et la
-- correspondance doit rester unique.

function Register()
    return "4C 8B DC 55 53 41 56 49 8D AB 28 FE FF FF 48 81 EC C0 02 00 00 48 8B"
end

function OnMatchFound(MatchAddress)
    return MatchAddress
end
