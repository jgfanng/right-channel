$(function() {
	// resource tab
	$('#resourceTab a:first').tab('show');
	$('#resourceTab').on('mouseenter', 'a', function(event) {
		event.preventDefault()
		$(this).tab('show')
	});
	
	// set interest: wish/dislike
    $('#setInterest').on('click', 'button', function(event) {
        var movieId = $(this).attr('data-movie-id');
        var interestType = $(this).attr('data-interest-type');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/interest'.format(movieId),
            data : {
                type: interestType
            }
        }).done(function() {
            $('#setInterest').addClass('hide');
            $('#removeInterest').removeClass('hide');
            if (interestType == 'wish') {
                $('#disliked').addClass('hide');
                $('#wished').removeClass('hide');
            } else if (interestType == 'dislike') {
                $('#wished').addClass('hide');
                $('#disliked').removeClass('hide');
            }
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    });
    
    // remove interest
    $('#removeInterest').on('click', 'button', function(event) {
        var movieId = $(this).attr('data-movie-id');
        $.ajax({
            type : 'DELETE',
            url : '/api/movie/{0}/interest'.format(movieId),
        }).done(function() {
            $('#removeInterest').addClass('hide');
            $('#setInterest').removeClass('hide');
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    });
    
    // set rating
    $('.star-rating-large').on('click', function(event) {
        var movieId = $(this).attr('data-movie-id');
        var rating = $(event.target).attr('data-rating');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/rating'.format(movieId),
            data : {
                rating: rating
            },
            context : this /* specify the DOM element as the context */
        }).done(function() {
            // remove previous rating
        	$(this).removeClass(function (index, css) {
        	    return (css.match (/\bstar-rating-large-v\S+/g) || []).join(' ');
        	});
        	// set new rating
        	$(this).addClass("star-rating-large-v" + rating * 2);
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    })
});