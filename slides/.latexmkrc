# LuaLaTeX; theme nằm trong ./hust-theme (đường dẫn thêm vào TEXINPUTS, cả Windows lẫn Linux/Overleaf)
$pdf_mode = 4;
$lualatex = 'lualatex -interaction=nonstopmode -file-line-error %O %S';
my $sep = ($^O eq 'MSWin32') ? ';' : ':';
$ENV{'TEXINPUTS'} = './hust-theme//' . $sep . ($ENV{'TEXINPUTS'} // '') . $sep;
$bibtex_use = 0;
