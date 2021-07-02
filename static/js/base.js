/*  ==========================================
    SHOW UPLOADED IMAGE
* ========================================== */
function readURL(input) {
    
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.readAsDataURL(input.files[0]);
        var fileName = input.files[0].name;
        var validFileExtensions = [".jpg", ".jpeg", ".bmp", ".gif", ".png"];
        //console.log("Check");
        //console.log(fileName);
        if (fileName.length > 0) {
              var blnValid = false;
              for (var j = 0; j < validFileExtensions.length; j++) {
                  var sCurExtension = validFileExtensions[j];
                  if (fileName.substr(fileName.length - sCurExtension.length, sCurExtension.length).toLowerCase() === sCurExtension.toLowerCase()) {
                      blnValid = true;
                      break;
                  }
              }
              
              if (!blnValid) {
                  //console.log("Result"+blnValid);
                  document.getElementById("upload-txt").innerHTML =  "<font color='#FF0000'> Sorry, " + fileName + " is invalid, allowed extensions are: " + validFileExtensions.join(", ") + "</font>";
                  $('#submit-btn').attr('disabled',true);
                  $('#submit-btn').css('cursor','no-drop');
                  //$("#up-img").html('');
                  $("#imageResult").attr('src','');
                  //return false;
              }
              else{
                document.getElementById("upload-txt").innerHTML = "Uploaded Image";
                $('#submit-btn').attr('disabled',false);
                $('#submit-btn').css('cursor','pointer');
                //$("#up-img").html('');
                $('#sol-txt').html('The solved sudoku image will be rendered inside the box below.');
                reader.onload = function (e) {
                    $('#imageResult')
                        .attr('src', e.target.result);            
                };
              }
          }


    }
    
    
}

    $(document).ready(function () { 
        $('#upload').on('change', function () {
            input = document.getElementById('upload');
            readURL(input);
        });
    });


$(document).ready(function() {

    $('#submit-btn').click(function(event){
    $('#submit-btn').attr('disabled',true);
    $('#submit-btn').css('cursor','no-drop');
    
    // Loading Overlay
    $.LoadingOverlay("show",{
        background  : "rgba(112, 108, 154, 0.6)",
        imageAutoResize         : true,
        imageResizeFactor : 3,
        imageAnimation          : "10000000ms rotate_left",  
        image : "./../static/images/img.gif"
        //fontawesome : "fa fa-tasks",
        //fontawesomeColor : "rgba(51 , 0, 51, 1)"
    }); 

    var post_url = '/solve_puzzle'; //get form action url
    var input = document.getElementById("upload");
    var img_file = input.files[0];
    var reader = new FileReader();
    var img_res;

    reader.readAsDataURL(img_file);
    reader.onload = function () {
        img_res   = reader.result;
         //console.log("Image readed!");

            $.ajax({
                url: post_url,
                contentType: 'application/json',
                dataType: "json",
                type: "POST",
                data: JSON.stringify({img_res: img_res}),
                success: function(response) {
                    resp = JSON.parse(JSON.stringify(response));
                    resp = resp.res;
                    if (resp ==  'No Puzzle Found, please use proper sudoku puzzle image'){
                            //console.log('Inside if Success '+ response);
                            document.getElementById('sol-txt').innerHTML = "<font color='#FF0000'>"+resp+"</font>";
                            $("#up-img").html('');
                            $('#submit-btn').attr('disabled',true);
                            $('#submit-btn').css('cursor','no-drop');
                    }
                    else if (resp ==  'No Solution Found'){
                        document.getElementById('sol-txt').innerHTML = "<font color='#FF0000'>"+resp+", please use proper sudoku puzzle image</font>";
                        $("#up-img").html('');
                        $('#submit-btn').attr('disabled',true);
                        $('#submit-btn').css('cursor','no-drop');
                    }
                    else if(resp == 'No response'){
                        document.getElementById('sol-txt').innerHTML = "<font color='#FF0000'>"+resp+"! Something Went wrong, try uploading proper sudoku puzzle image</font>";
                        $("#up-img").html('');
                        $('#submit-btn').attr('disabled',true);
                        $('#submit-btn').css('cursor','no-drop');
                    }
                    else{
                    //console.log('Inside Else');
                    result_img = '<img id="imageSolved" src= "data:image/jpeg;base64,'+resp+'" alt="sudoku solver image" class="img-fluid rounded shadow-sm mx-auto d-block"></img>'
                    //$("#up-img").html(result_img);
                    //document.getElementById("up-img").style.display="none";
                    document.getElementById('upload-txt').innerHTML =  "Sudoku Puzzle Solution</font>";
                    $("#up-img").html(result_img);
                    $('#submit-btn').attr('disabled',false);
                    $('#submit-btn').css('cursor','pointer');
                    }
                    $.LoadingOverlay("hide"); 
                  
                },
                
                error: function(xhr) {
                //Do Something to handle error
                document.getElementById('sol-txt').innerHTML = "<font color='#FF0000'>Something Went wrong, try uploading proper sudoku puzzle image</font>";
                $("#up-img").html('');
                $('#submit-btn').attr('disabled',true);
                $('#submit-btn').css('cursor','no-drop');
                $.LoadingOverlay("hide"); 
                }

            });
            
        


        };
    reader.onerror = function(){
        //console.log(reader.error);
        document.getElementById("upload-txt").innerHTML =  "<font color='#FF0000'> Sorry, " + fileName + " is unable to read </font>";
    };    
   
   
    }); 

});
