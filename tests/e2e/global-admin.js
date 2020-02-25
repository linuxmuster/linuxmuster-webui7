var auth = require('./authconfig.json');

describe('lmn landingpage connect', function() {
    it('should show the loading page as global-admin', function() {
        browser.get(auth.url);

        element(by.model('username')).sendKeys(auth.admin.login);
        element(by.model('password')).sendKeys(auth.admin.pw);
        element(by.css('a[ng\\:click^="login"]')).click();
        browser.sleep(8000);
        expect(element.all(by.tagName('h2')).first().getText()).toContain('Linuxmuster.net 7');

    });
});

describe('lmn disconnect', function() {
    it('should show the login page again', function() {
        element(by.css('a[uib-dropdown-toggle]')).click();
        element(by.css('a[ng\\:click^="identity.logout"]')).click();
        browser.sleep(5000);
        expect(element.all(by.tagName('input')).first().getAttribute('ng:model')).toContain('username');

    });
});