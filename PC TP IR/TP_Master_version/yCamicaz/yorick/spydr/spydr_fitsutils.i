func E2880(i)
/* DOCUMENT j = E2880(i)
     returns the first multiple of 2880 greater or equal than i
   SEE ALSO:
 */
{
  return (1l+(long(i)-1l)/2880l)*2880l;
}

func retspace(i)
/* DOCUMENT str = retspace(i)
     Returns a string of <i> whitespaces.
   SEE ALSO:
 */
{
  if(i<1) return "";
  return string(&array(' ',i));
}

func fill80(str, k)
/* DOCUMENT fill80(str, k)
     Complement right part of string <str> with
     whitespaces up to a total of <k> characters.
     <k> can be omitted, default value is 80.
   SEE ALSO:
 */
{
  if( is_void(k) ) k=80;
  l = strlen(str);
  if( l>k ) {
    return strpart(str,1:k);
  }
  return str+retspace(k-l);
}

func pref80(str, k)
/* DOCUMENT fill80(str, k)
     Complement left part of string <str> with
     whitespaces up to a total of <k> characters.
     <k> can be omitted, default value is 80.
   SEE ALSO:
 */
{
  if( is_void(k) ) k=80;
  l = strlen(str);
  if( l>k ) {
    return strpart(str,l-k+1:l);
  }
  return retspace(k-l) + str;
}

func int2str(i)
/* DOCUMENT my_string = int2str(i)
     Converts an integer to a string.
   SEE ALSO:
 */
{
  if( checkRange(i,comment="integer value",function="int2str") )
    exit;
  return swrite(format="%d",long(i));
}

func var2str(xvalue)
/* DOCUMENT str = var2str(x)
     Converts an array of numbers (floats, double or long) into string array.
     Keeps a
   SEE ALSO:
 */
{
  tx=typeof(xvalue);
  if(tx=="string") return xvalue;
  value = [];
  if(tx=="char"|tx=="int"|tx=="long"|tx=="short") {
    value = swrite(format="%d",long(xvalue));
  }
  if(tx=="float"|tx=="double") {
    value = swrite(format="%g",double(xvalue));
  }
  return value;
}


func writefits(fichier, data, keyword, xvalue, comment=)
/* DOCUMENT writefits, fichier, data, keyword, value, comment=
   Writes <data> in the the file called <fichier>.
   Optionally, one can provide it with some keywords with the associated
   values, and comments.

   Examples:
   writefits, "myfile.fits", data;
   writefits, "myfile.fits", data, ["DATE","OBSERVER"],[fitsDate(),"Bob"], comment="just a joke"
   writefits, "myfile.fits", data, "DATE",fitsDate(), comment=["just a joke","really !"]
   
   SEE ALSO:
 */
{
  fic = open( fichier, "wb+");
  if( !fic ) {
    write,format="Can't open file %s. Exiting now. Nothing written.\n",fichier;
    error;
  }
  sun_primitives,fic;

  ptr = 0;
  if( typeof(data)=="pointer" ) {
    nextend = numberof(data);
    core_writefits, fic, ptr, nextend, [], keyword, xvalue, comment=comment;
    for(i=1;i<=nextend;i++) {
      //      write,format="extension %d at ptr=%d \n",i,ptr;
      core_writefits, fic, ptr, nextend, *data(i);
    }
  } else {
    core_writefits, fic, ptr, 0, data, keyword, xvalue, comment=comment;
  }
  close, fic;
  return 0;
}



func writeFitsField(fic, ptr, keyword, value, comment)
{
  if( keyword=="COMMENT" ) {
    tmp = fill80( "COMMENT " + comment );
  } else if( keyword=="END" ) {
    tmp = fill80("END");
  } else if( keyword==" " ) {
    tmp = fill80(" ");
  } else {
    tmp = fill80( fill80(keyword,8) + "=" + pref80( var2str(value),21) + " / "+comment );
  }
  // write,format="%d:%s\n",ptr,tmp;
  _write, fic, ptr, strchar(tmp);
  ptr += 80;
  return ptr;
}

func core_writefits(fichier, &ptr, nextend, data, keyword, xvalue, comment=)
/* DOCUMENT writefits, fichier, data, keyword, value, comment=
   Writes <data> in the the file called <fichier>.
   Optionally, one can provide it with some keywords with the associated
   values, and comments.

   Examples:
   writefits, "myfile.fits", data;
   writefits, "myfile.fits", data, ["DATE","OBSERVER"],[fitsDate(),"Bob"], comment="just a joke"
   writefits, "myfile.fits", data, "DATE",fitsDate(), comment=["just a joke","really !"]
   
   SEE ALSO:
 */
{
  bitpix=0;
  value = var2str( xvalue );  // converts xvalue into a string

  // if data==[], no data should be written: only the header of extensions should be written
  if( nextend==0 ) {
    status="simple+data";
    if( data==[] )
      return -1;
  }
  else {
    if( data==[] )
      status="global-extension";
    else
    status="extension+data";
  }

  if( status!="global-extension" ) {
    // we inted to write the data ...
    datatype = typeof(data);
    if( datatype=="double" ) bitpix=-64;
    if( datatype=="float" ) bitpix=-32;
    if( datatype=="long" ) bitpix=32;
    if( datatype=="int" ) bitpix=32;
    if( datatype=="short" ) bitpix=16;
    if( datatype=="char" ) bitpix=8;
    if( !bitpix ) {
      write,format="Error : unknown data type %s \n",datatype;
      error;
    }
    dim = dimsof(data);
  }
  
  if( status=="simple+data" ) {
    ptr = writeFitsField(fic, ptr, "SIMPLE", "T", "Std FITS");
  }

  if( status=="extension+data" ) {
    ptr = writeFitsField(fic, ptr, "XTENSION", "'IMAGE '", "extension ...");
  }
  
  if( status!="global-extension" ) {
    ptr = writeFitsField(fic, ptr, "BITPIX", bitpix, "Yorick "+typeof(data));
    naxis = dim(1);
    ptr = writeFitsField(fic, ptr, "NAXIS", naxis, "Number of axes");
    for(i=1; i<=naxis;i++) {
      ptr = writeFitsField(fic, ptr, "NAXIS"+int2str(i), dim(i+1), "Axis "+int2str(i));
    }
  }
  
  if( status=="global-extension" ) {
    ptr = writeFitsField(fic, ptr, "SIMPLE", "T", "Std FITS");
    ptr = writeFitsField(fic, ptr, "BITPIX", 8, "Useless");
    ptr = writeFitsField(fic, ptr, "NAXIS", 0, "No data in primary header");
    ptr = writeFitsField(fic, ptr, "EXTEND", "T", "Extended FITS");
    ptr = writeFitsField(fic, ptr, "NEXTEND", nextend, "Nber of extensions");
  }
  
  // WRITING KEYWORDS
  nk = numberof(keyword);
  nval = numberof(value);
  if( nval!=nk ) {
    write,format="WARNING : numberof keyword (%d) different from number of values (%d)\n", nk, nval;
    nk = min(nk,nval);
    write,format="WARNING : only (%d) values will be written\n", nk;
  }
  for(i=1; i<=nk; i++) {
    ptr =  writeFitsField(fic, ptr, keyword(i), value(i), " ");
  }

  // WRITING COMMENTS
  if( !is_void(comment) ) {
    nc = numberof(comment);
    for(i=1;i<=nc;i++) {
      ptr =  writeFitsField(fic, ptr, "COMMENT", 0 , comment(i));
    }
  }
  ptr =  writeFitsField(fic, ptr, "END", 0,0);

  // FILLING THE HEADER WITH ' '  ..........    // 'LE' bug du mercredi 24 Novembre 2010
  npad = E2880(ptr) - ptr;
  if( npad ) {
    tmp = array(' ', npad);
    _write, fic, ptr, tmp;
    ptr += npad;
  }

  // WRITING DATA
  if( status!="global-extension" ) {
    _write,fic,ptr,data;
    // ptr += sizeof(data);   // cree un bug sur une architecture 64 bits car sizeof(long(0))=8
    ptr += numberof(data) * abs(bitpix)/8;
  }

  
  // zero-padding ....
  npad = E2880(ptr) - ptr;
  if( npad ) {
    tmp = array(char(0), npad);
    _write, fic, ptr, tmp;
    ptr += npad;
  }
  // write,format="ptr in core_writefits = %d \n",ptr;
  return 0;
}



