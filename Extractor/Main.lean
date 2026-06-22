import Lean

open Lean
open Lean.Meta

structure TheoremData where
  name : String
  module : String
  docstring : String
  proposition : String
  proof : String
  deriving ToJson

structure PreflightData where
  total_theorems : Nat
  deriving ToJson

def extractTheorems (targetModNames : Array Name) : MetaM Unit := do
  let env ← getEnv

  let mut lst := #[]
  lst := lst ++ env.constants.map₁.toArray
  lst := lst ++ env.constants.map₂.toArray

  let mut totalCount := 0
  for (name, cinfo) in lst do
    if let ConstantInfo.thmInfo _ := cinfo then
      let modOpt ← findModuleOf? name
      if let some mod := modOpt then
        if targetModNames.contains mod then
          let nameStr := toString name
          if not (nameStr.startsWith "_" || nameStr.contains '✝' || nameStr.contains ".proof_" || nameStr.contains "._proof_" || nameStr.contains ".eq_" || nameStr.contains ".match_") then
            totalCount := totalCount + 1

  let preflight : PreflightData := { total_theorems := totalCount }
  IO.println (toJson preflight |>.compress)

  for (name, cinfo) in lst do
    if let ConstantInfo.thmInfo val := cinfo then
      let modOpt ← findModuleOf? name
      if let some mod := modOpt then
        if targetModNames.contains mod then
          let nameStr := toString name

          if not (nameStr.startsWith "_" || nameStr.contains '✝' || nameStr.contains ".proof_" || nameStr.contains "._proof_" || nameStr.contains ".eq_" || nameStr.contains ".match_") then
            let doc ← findDocString? env name
            let docStr := doc.getD ""

            let typeStr := toString val.type
            let valStr := toString val.value

            let data : TheoremData := {
              name := nameStr,
              module := toString mod,
              docstring := docStr,
              proposition := typeStr,
              proof := valStr
            }

            IO.println (toJson data |>.compress)

def main (args : List String) : IO Unit := do
  if args.isEmpty then
    IO.println "{\"error\": \"Aucun module spécifié\"}"
    return

  initSearchPath (← Lean.findSysroot)

  let modNames := args.toArray.map String.toName
  let imports := modNames.map (fun m => { module := m : Import })

  let env ← importModules imports {}

  let coreCtx : Core.Context := { fileName := "extractor", fileMap := default, maxHeartbeats := 0 }
  let coreState : Core.State := { env := env }
  let metaCtx : Meta.Context := {}
  let metaState : Meta.State := {}

  let _ ← (extractTheorems modNames |>.run metaCtx metaState).toIO coreCtx coreState
