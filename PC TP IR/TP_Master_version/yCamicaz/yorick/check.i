require, "yCamicaz.i";
  
cam = camicaz_new("camicaz.ini");
img = camicaz_get_image(cam);
cam = [];
window, 1;
pli, img(,,1);
pltitle, "reset frame";
//colorbar, min(img(,,1)), max(img(,,1));
window, 2;
pli, img(,,2);
pltitle, "int frame";
//colorbar, min(img(,,2)), max(img(,,2));

aaa = img(,,2)-img(,,1);
window, 3;
pli, aaa
pltitle, "int-reset frame"
//colorbar, min(aaa), max(aaa);
