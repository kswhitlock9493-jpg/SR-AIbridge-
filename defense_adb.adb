-- defense_adb.adb - NATO STANAG 4586 Safety Crate (Ada 2022)
with Ada.Numerics.Elementary_Functions; use Ada.Numerics.Elementary_Functions;

package Defense_CR is
   type Defense_Context is record
      Scores  : Float_Array (1 .. 8) := (others => 0.0);
      Weights : Float_Array (1 .. 8) := (0.30, 0.25, 0.20, 0.15, 0.10, others => 0.0);
      Count   : Natural := 5;
   end record;

   function Calculate_Mu (Ctx : Defense_Context) return Float;
   function Check_CH return Boolean;
   type Weapons_Decision is (WEAPONS_GO, WEAPONS_HALT);
   function Evaluate_Defense_Harmony (Mu : Float; Ch : Boolean) return Weapons_Decision;
end Defense_CR;

package body Defense_CR is
   function Calculate_Mu (Ctx : Defense_Context) return Float is
      Log_Sum : Float := 0.0;
   begin
      for I in 1 .. Ctx.Count loop
         declare
            S : Float := Float'Max (Float'Min (Ctx.Scores(I), 1.0), 1e-12);
         begin
            Log_Sum := Log_Sum + Ctx.Weights(I) * Log (S);
         end;
      end loop;
      return Exp (Log_Sum);
   end Calculate_Mu;

   function Check_CH return Boolean is
   begin
      return No_Friendly_Fire_Vector and
             Crypto_Ignition_Valid and
             ROE_Flag_Green and
             Supply_Chain_Attested and
             Commander_Biometric_OK and
             EW_Threat_Yellow_Or_Less;
   end Check_CH;

   function Evaluate_Defense_Harmony (Mu : Float; Ch : Boolean) return Weapons_Decision is
   begin
      if Mu >= 0.9995 and Ch then
         return WEAPONS_GO;
      else
         Trigger_Autoheal;
         Log_Harmony_Fault (Mu, Ch);
         return WEAPONS_HALT;
      end if;
   end Evaluate_Defense_Harmony;
end Defense_CR;
