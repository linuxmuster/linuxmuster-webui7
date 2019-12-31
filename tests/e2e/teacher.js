var auth = require('./authconfig.json');

describe('lmn landingpage connect', function() {
    it('should show the loading page as teacher', function() {
        browser.get(auth.url);

        element(by.model('username')).sendKeys(auth.teacher.login);
        element(by.model('password')).sendKeys(auth.teacher.pw);
        element(by.linkText('Log in')).click();
        //console.log('Click is done !');
        browser.sleep(5000);
        expect(element.all(by.tagName('h2')).first().getText()).toContain('Linuxmuster.net 7');
    });
});



