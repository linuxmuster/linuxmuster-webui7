var auth = require('./authconfig.json');

describe('lmn landingpage connect', function() {
    it('should show the loading page as global-admin', function() {
        browser.get(auth.url);

        element(by.model('username')).sendKeys(auth.admin.login);
        element(by.model('password')).sendKeys(auth.admin.pw);
        element(by.linkText('Log in')).click();
        //console.log('Click is done !');
        browser.sleep(5000);
        expect(element.all(by.tagName('h2')).first().getText()).toContain('Linuxmuster.net 7');

    });
});
