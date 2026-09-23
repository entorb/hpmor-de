# latexmk configuration to build HPMOR -*- mode: perl -*-

use Config;
use File::Spec::Functions;

# A bare `latexmk` builds the one-volume PDF only. The six volumes and the
# dust jackets are built by GitHub Actions, or on demand by name, e.g.
# `latexmk hpmor-3` / `latexmk layout/hpmor-dust-jacket-3`.
@default_files = ('hpmor');

# Use XeLaTeX (equivalent to command-line -xelatex option)
$xelatex = "xelatex %O \"\\PassOptionsToPackage{$options}{hp-book}\\input{%S}\"" if $options;
my $basedir = curdir();
if (defined($chapter) || defined($chapterfile)) {
  if (defined($chapter)) {
    die "Not in `chapters' directory" if !-d catdir('..', '.git');
    $basedir = updir();
    $ENV{TEXINPUTS} = ".$Config{path_sep}$basedir$Config{path_sep}";
    $chapterfile = 'hpmor-chapter-' . sprintf('%03d', $chapter);
  } else {
    $chapter = 1;
  }
  $xelatex = "xelatex -jobname=$chapterfile %O \"\\RequirePackage[pdf]{layout/hp-book}\\begin{document}\\setcounter{chapter}{" . ($chapter - 1) . "}\\input{$chapterfile}\\end{document}\"";
}
$pdf_mode = 5;
$postscript_mode = $dvi_mode = 0;

# Make our fonts available to TeX
$ENV{TEXFONTS} = catfile($basedir, 'fonts') . catfile('', '') x 2 . $Config{path_sep};
