$(function() {
	// resource tab
	$('#resourceTab a:first').tab('show');
	$('#resourceTab').on('mouseenter', 'a', function(event) {
		event.preventDefault()
		$(this).tab('show')
	});
	
    $('.interest-unmarked').on('click', 'button', function(event) {
        var movieId = $(this).attr('data-movie-id');
        var interestType = $(this).attr('data-interest-type');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/interest'.format(movieId),
            data : {
                type: interestType
            }
        }).done(function() {
            $('.interest-unmarked').hide();
            $('.interest-marked').fadeIn();
            
            var interestDescs = new Array();
            interestDescs['wish'] = '想看';
            interestDescs['dislike'] = '没兴趣';
            $('.interest-marked').children('.interest-desc').text('已标记为' + interestDescs[interestType]);
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    });
    
    $('.interest-marked').on('click', 'button', function(event) {
        var movieId = $(this).attr('data-movie-id');
        $.ajax({
            type : 'DELETE',
            url : '/api/movie/{0}/interest'.format(movieId),
        }).done(function() {
            $('.interest-marked').hide();
            $('.interest-unmarked').fadeIn();
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    });
    
    // click on star-rating-large
    $('.star-rating-large').on('click', function(event) {
        var movieId = $(this).attr('data-movie-id');
        var rating = $(event.target).attr('data-rating');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/rating'.format(movieId),
            data : {
                rating: rating
            }
        }).done(function() {
        	$(this).removeClass(function(index, css) {
        	    var re = new RegExp("-\\d+");
        	    return (css.match(re) || []).join(' ');
        	});
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    })
});