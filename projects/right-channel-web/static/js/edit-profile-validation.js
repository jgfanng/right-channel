$(function() {
	// nick name validation
	$('#nickName').focus(function(event) {
		$('#nickNameHelp').text('请输入您在网上的常用昵称，不多于12个字符');
		$('#nickNameHelp').attr('class', 'help-inline help-info');
		$('#nickNameHelp').show();
	});

	$('#nickName').blur(function(event) {
		var $target = $(event.target);
		var value = $.trim($target.val());

		if (value.length == 0) {
			$('#nickNameHelp').text('昵称不能为空');
			$('#nickNameHelp').attr('class', 'help-inline help-error');
			$('#nickNameHelp').show();
		} else if (value.length > 12) {
			$('#nickNameHelp').text('昵称不多于12个字符');
			$('#nickNameHelp').attr('class', 'help-inline help-error');
			$('#nickNameHelp').show();
		} else {
			$('#nickNameHelp').text('');
			$('#nickNameHelp').attr('class', 'help-inline help-info');
			$('#nickNameHelp').hide();
		}
	});

	// form submission validation
	$('#editProfile').submit(function() {
		var nickNameValue = $.trim($('#nickName').val());

		if (nickNameValue.length > 0 && nickNameValue.length <= 12)
			return true;
		else {
			$('#submitHelp').text('您输入的昵称不正确，请重新输入')
			$('#submitHelp').attr('class', 'help-inline help-error');
			$('#submitHelp').show().fadeOut(3000);
			return false;
		}
	});
});