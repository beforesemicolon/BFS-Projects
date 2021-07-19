{
	const registerForm = document.getElementById('register-form');

	if (registerForm) {
		const fieldsetList = registerForm.querySelectorAll('fieldset');
		let currentSetIndex = Math.max(
			Array
				.from(fieldsetList)
				.findIndex(fs => fs.classList.contains('has-error')),
			0
		);
		let currentFieldset = fieldsetList[currentSetIndex];

		fieldsetList.forEach((fieldset, i) => {
			fieldset.style.display = i === currentSetIndex ? 'block' : 'none';
			fieldset.style.animation = 'slide 0.5s ease forwards';
		})

		const submitBtn: HTMLElement | null = registerForm.querySelector('.submit');
		const nextBtn: HTMLElement | null = registerForm.querySelector('.next');
		const prevBtn: HTMLElement | null = registerForm.querySelector('.prev');

		if (submitBtn && nextBtn && prevBtn) {
			const navigate = (index: number) => {
				if (index === fieldsetList.length - 1) {
					submitBtn.style.display = 'block';
					prevBtn.style.display = 'block';
					nextBtn.style.display = 'none';
				} else {
					submitBtn.style.display = 'none';
					prevBtn.style.display = index === 0 ? 'none' : 'block';
					nextBtn.style.display = 'block';
				}

				currentFieldset.style.display = 'none';
				fieldsetList[index].style.display = 'block';
				currentFieldset = fieldsetList[index];
				// immediately focus on the first input field in the fieldset
				currentFieldset.querySelector('input')?.focus();
			}

			nextBtn.addEventListener('click', () => {
				currentSetIndex = (currentSetIndex + 1) % fieldsetList.length;
				navigate(currentSetIndex);
			})

			prevBtn.addEventListener('click', () => {
				currentSetIndex = (currentSetIndex - 1) % fieldsetList.length;
				navigate(currentSetIndex);
			})

			registerForm.addEventListener('submit', (event) => {
				// if the user presses the return key in the middle of
				// form filling it should detect and make sure the last
				// fieldset is showing before trying to submit
				// otherwise we simply move to the next fieldset to be filled
				if (currentSetIndex < fieldsetList.length - 1) {
					event.preventDefault();
					currentSetIndex += 1;
					navigate(currentSetIndex);
				}
			})

			navigate(currentSetIndex);
		}
	}
}
