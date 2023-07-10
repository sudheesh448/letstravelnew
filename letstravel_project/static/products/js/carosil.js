$(document).ready(function(){
	 
    //Show carousel-control
    
    $("#myCarousel").mouseover(function(){
        $("#myCarousel .carousel-control").show();
    });

    $("#myCarousel").mouseleave(function(){
        $("#myCarousel .carousel-control").hide();
    });
    
    //Active thumbnail
    
    $("#thumbCarousel .thumb").on("click", function(){
        $(this).addClass("active");
        $(this).siblings().removeClass("active");
    
    });
    
    //When the carousel slides, auto update
    
    $('#myCarousel').on('slid.bs.carousel', function(){
       var index = $('.carousel-inner .item.active').index();
       //console.log(index);
       var thumbnailActive = $('#thumbCarousel .thumb[data-slide-to="'+index+'"]');
       thumbnailActive.addClass('active');
       $(thumbnailActive).siblings().removeClass("active");
       //console.log($(thumbnailActive).siblings()); 
    });
 });