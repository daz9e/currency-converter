{
  description = "Money Convert - Telegram bot for currency conversion";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python312;
          pythonPackages = python.pkgs;
        in
        {
          default = pythonPackages.buildPythonApplication {
            pname = "money-convert";
            version = "0.1.0";
            format = "other";

            src = ./.;

            propagatedBuildInputs = with pythonPackages; [
              python-telegram-bot
              requests
            ];

            installPhase = ''
              mkdir -p $out/lib/money-convert
              cp bot.py currency.py $out/lib/money-convert/

              mkdir -p $out/bin
              cat > $out/bin/money-convert <<EOF
              #!${python}/bin/python
              import sys
              sys.path.insert(0, "$out/lib/money-convert")
              exec(open("$out/lib/money-convert/bot.py").read())
              EOF
              chmod +x $out/bin/money-convert
            '';
          };
        }
      );

      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.money-convert;
        in
        {
          options.services.money-convert = {
            enable = lib.mkEnableOption "Money Convert Telegram bot";

            tokenFile = lib.mkOption {
              type = lib.types.path;
              description = "Path to a file containing the Telegram bot token";
              example = "/run/secrets/money-convert-token";
            };

            defaultCurrency = lib.mkOption {
              type = lib.types.str;
              default = "EUR";
              description = "Default currency code (EUR, RUB, UAH, RSD)";
            };
          };

          config = lib.mkIf cfg.enable {
            systemd.services.money-convert = {
              description = "Money Convert Telegram Bot";
              wantedBy = [ "multi-user.target" ];
              after = [ "network-online.target" ];
              wants = [ "network-online.target" ];

              serviceConfig = {
                Type = "simple";
                DynamicUser = true;
                Restart = "always";
                RestartSec = 10;

                # Hardening
                NoNewPrivileges = true;
                ProtectSystem = "strict";
                ProtectHome = true;
                PrivateTmp = true;
              };

              environment = {
                DEFAULT_CURRENCY = cfg.defaultCurrency;
              };

              script = ''
                export TELEGRAM_BOT_TOKEN=$(cat ${cfg.tokenFile})
                exec ${self.packages.${pkgs.system}.default}/bin/money-convert
              '';
            };
          };
        };
    };
}
