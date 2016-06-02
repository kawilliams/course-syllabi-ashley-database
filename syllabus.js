var options = {
  valueNames: [ 'name', 'number', 'professor' ]
};

var userList = new List('users', options);

$(document).ready(function(){
  $("#hideme").click(function(){
    $(".novisit").toggle();
  });
  
  $("#prof").click(function(){
    $("#prof_list").toggle();
    $("#down_arrow").toggle();
    $("#side_arrow").toggle();
  });
});
