function deletePost(postid){
  $.ajax('/delete-post', {
    type: 'POST',
    data: {
      postid: postid
    }
  });
}
/*function showPostSettings(postid){
  $.ajax('/find', {
    type: 'GET',
    data: {
      postid: postid
    }
  });
}*/

function Comment(comment, postid){
  console.log('Post request recieved');
  if(comment.val()===""){
    console.log("Went into this")
    event.preventDefault()
    return false;
  }
  $(".overlay").show();
  $.ajax('/p/' + postid, {
    type: 'POST',
    data: {
      commenti: comment.val()
    },
    success: function(data){
      console.log("Comment posted")
      var id = data.substr(0, data.indexOf(' '));
      var code = data.substr(data.indexOf(' ')+1);
      $('#' + id).find('.post-content').append(code);
      $('#' + id).find('#comment').val("");
      $(".overlay").hide();
    }
  });
  event.preventDefault();
  return false;
}
/*onClick="this.setSelectionRange(0, this.value.length)"*/
