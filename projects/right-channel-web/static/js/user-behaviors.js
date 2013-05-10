function userBehaviorMark($btn) {
	var movieId = $btn.attr('data-movie-id');
	var behaviorType = $btn.attr('data-behavior-type');
	$.ajax({
		type : 'post',
		url : '/api/movie/userbehavior',
		data : {
			movie_id : movieId,
			behavior_type: behaviorType
		}
	}).done(function() {
		$btn.parent().children('.marked-hint').show();
		$btn.parent().children('.marked').show();
		$btn.parent().children('.unmarked').hide();
		
		var user_behaviors = new Array();
		user_behaviors['to_watch'] = '想看';
		user_behaviors['watched'] = '看过';
		user_behaviors['not_interested'] = '没兴趣';
		$btn.parent().children('.marked-hint').text('已标记为' + user_behaviors[behaviorType]);
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		}
	});
}

function userBehaviorUnmark($btn) {
	var movieId = $btn.attr('data-movie-id');
	$.ajax({
		type : 'delete',
		url : '/api/movie/userbehavior/' + movieId
	}).done(function() {
		$btn.parent().children('.marked-hint').hide();
		$btn.parent().children('.marked').hide();
		$btn.parent().children('.unmarked').show();
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		}
	});
}

function rating(movieId, rating) {
	$.ajax({
		type : 'post',
		url : '/api/movie/rating',
		data : {
			movie_id : movieId,
			rating: rating
		}
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		}
	});
}