function required() 
   {
    let empt = document.forms["form1"]["text1"].value;
     if (inputtx.value.length == 0)
      { 
         alert("message");  	
         return false; 
      }  	
      return true; 
    }