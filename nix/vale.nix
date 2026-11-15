# Vale bundled with its styles, so `nix run .#vale` needs no `vale sync`.
# Adds this repository's own styles under .vale/styles and the -ise en_GB
# Hunspell dictionary for British spelling, and the Generic vocabulary that
# technical-writing ships, so the repository checks itself with it.
{ pkgs }:
pkgs.symlinkJoin {
  name = "vale-with-skills-styles-${pkgs.vale.version}";
  paths = [
    pkgs.vale
    pkgs.valeStyles.write-good
    pkgs.valeStyles.proselint
  ];
  nativeBuildInputs = [ pkgs.makeBinaryWrapper ];
  postBuild = ''
    styles=$out/share/vale/styles
    cp -r --no-preserve=mode ${../.vale/styles}/. $styles/
    # The vocabulary the technical-writing skill installs for other repositories
    cp -r --no-preserve=mode ${../skills/technical-writing/assets/vale/styles/config/vocabularies}/. $styles/config/vocabularies/
    mkdir -p $styles/config/dictionaries
    ln -s ${pkgs.hunspellDicts.en_GB-ise}/share/hunspell/en_GB.{aff,dic} $styles/config/dictionaries/
    wrapProgram $out/bin/vale --set VALE_STYLES_PATH $styles
  '';
  meta.mainProgram = "vale";
}
