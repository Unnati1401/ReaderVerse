$("label").click(function(){
    $(this).parent().find("label").css({"background-color": "#9a9191"});
    $(this).css({"background-color": "#d9e719"});
    $(this).nextAll().css({"background-color": "#d9e719"});
});
  
// $('.ratings_stars').click(function() {
//     $('.ratings_stars').removeClass('selected'); // Removes the selected class from all of them
//     $(this).addClass('selected'); // Adds the selected class to just the one you clicked
 
//     var rating = $(this).data('rating'); // Get the rating from the selected star
//     $('#ratingID').val(rating); // Set the value of the hidden rating form element
// });
 
function setRating(id) {
    $('.ratings_stars').removeClass('selected'); // Removes the selected class from all of them
    $(this).addClass('selected'); // Adds the selected class to just the one you clicked
 
    var rating = $(this).data('rating'); // Get the rating from the selected star
    $('#id').val(rating); // Set the value of the hidden rating form element
    console.log(id);
}