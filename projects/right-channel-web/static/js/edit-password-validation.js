$(function() {
	// old password validation
	$('#oldPassword').focus(function(event) {
		$('#oldPasswordHelp').text('6-16个字符，建议使用字母、数字或符号的组合');
		$('#oldPasswordHelp').attr('class', 'help-inline help-info');
		$('#oldPasswordHelp').show();
	});

	$('#oldPassword').blur(function(event) {
		var $target = $(event.target);
		var value = $target.val();

		if (value.length == 0) {
			$('#oldPasswordHelp').text('密码不能为空');
			$('#oldPasswordHelp').attr('class', 'help-inline help-error');
			$('#oldPasswordHelp').show();
		} else if (value.length < 6) {
			$('#oldPasswordHelp').text('密码不足6个字符');
			$('#oldPasswordHelp').attr('class', 'help-inline help-error');
			$('#oldPasswordHelp').show();
		} else if (value.length > 16) {
			$('#oldPasswordHelp').text('密码不多于16个字符');
			$('#oldPasswordHelp').attr('class', 'help-inline help-error');
			$('#oldPasswordHelp').show();
		} else {
			$('#oldPasswordHelp').text('');
			$('#oldPasswordHelp').attr('class', 'help-inline help-info');
			$('#oldPasswordHelp').hide();
		}
	});

	// new password validation
	$('#newPassword').focus(function(event) {
		$('#newPasswordHelp').text('6-16个字符，建议使用字母、数字或符号的组合');
		$('#newPasswordHelp').attr('class', 'help-inline help-info');
		$('#newPasswordHelp').show();
	});

	$('#newPassword').blur(function(event) {
		var $target = $(event.target);
		var value = $target.val();

		if (value.length == 0) {
			$('#newPasswordHelp').text('密码不能为空');
			$('#newPasswordHelp').attr('class', 'help-inline help-error');
			$('#newPasswordHelp').show();
		} else if (value.length < 6) {
			$('#newPasswordHelp').text('密码不足6个字符');
			$('#newPasswordHelp').attr('class', 'help-inline help-error');
			$('#newPasswordHelp').show();
		} else if (value.length > 16) {
			$('#newPasswordHelp').text('密码不多于16个字符');
			$('#newPasswordHelp').attr('class', 'help-inline help-error');
			$('#newPasswordHelp').show();
		} else {
			$('#newPasswordHelp').text('');
			$('#newPasswordHelp').attr('class', 'help-inline help-info');
			$('#newPasswordHelp').hide();
		}
	});

	// form submission validation
	$('#editPassword').submit( function() {
		var oldPasswordValue = $('#oldPassword').val();
		var newPasswordValue = $('#newPassword').val();

		if (oldPasswordValue.length >= 6 && oldPasswordValue.length <= 16 &&
			newPasswordValue.length >= 6 && newPasswordValue.length <= 16)
			return true;
		else {
			$('#submitHelp').text('您输入的旧密码或新密码不正确，请重新输入')
			$('#submitHelp').attr('class', 'help-inline help-error');
			$('#submitHelp').show().fadeOut(3000);
			return false;
		}
	});
});