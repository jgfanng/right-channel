$(function() {
  var threshold = 100;
  var next_page = 2;
  var has_more = true;
	$(window).scroll(function() {
		if ($(window).scrollTop() >= $(document).height() - $(window).height() - threshold) {
		  if (has_more) {
		    qs = {
	        genre: $('#genre').attr('data-genre'),
	        country: $('#country').attr('data-country'),
	        year: $('#year').attr('data-year'),
	        sort: $('#sort').attr('data-sort'),
	        resource: $('#resource').attr('data-resource'),
	        page: next_page
		    };
	      $.getJSON('/api/movie', qs, function(data) {
	        next_page = next_page + 1;
	        has_more = data.has_more;
	      });
	    }
		}
	});
});