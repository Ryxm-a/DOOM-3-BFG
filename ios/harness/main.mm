// SPDX-License-Identifier: GPL-3.0-or-later
// Phase 02 application harness. The engine is not linked into this target.
#import <UIKit/UIKit.h>
#import <TargetConditionals.h>
#include <cstdint>

static_assert(sizeof(void *) == 8, "The harness requires a 64-bit target");
static_assert(sizeof(std::uint32_t) == 4, "Unexpected fixed-width integer size");
extern "C" const char *BFG_RunCoreTests();

@interface HarnessViewController : UIViewController
@end

@implementation HarnessViewController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = [UIColor colorWithRed:0.07 green:0.08 blue:0.10 alpha:1.0];
    UILabel *label = [[UILabel alloc] init];
    label.text = @"DOOM 3 BFG\niOS port harness - Phase 03a\n\nCore idlib fixtures run here.\nEngine and gameplay are not integrated.";
    label.textColor = UIColor.whiteColor;
    label.textAlignment = NSTextAlignmentCenter;
    label.font = [UIFont systemFontOfSize:22 weight:UIFontWeightMedium];
    label.numberOfLines = 0;
    label.translatesAutoresizingMaskIntoConstraints = NO;
    label.accessibilityIdentifier = @"phase02-harness-status";
    [self.view addSubview:label];
    UILayoutGuide *safe = self.view.safeAreaLayoutGuide;
    [NSLayoutConstraint activateConstraints:@[
        [label.centerXAnchor constraintEqualToAnchor:safe.centerXAnchor],
        [label.centerYAnchor constraintEqualToAnchor:safe.centerYAnchor],
        [label.leadingAnchor constraintGreaterThanOrEqualToAnchor:safe.leadingAnchor constant:24],
        [label.trailingAnchor constraintLessThanOrEqualToAnchor:safe.trailingAnchor constant:-24]
    ]];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
#if TARGET_OS_SIMULATOR
    // CI supplies a fresh nonce. A receipt from viewDidAppear proves app code ran,
    // beyond simctl merely accepting a launch request. Never emitted on device.
    NSString *nonce = NSProcessInfo.processInfo.environment[@"BFG_HARNESS_NONCE"];
    if (nonce.length > 0) {
        const char *coreResult = BFG_RunCoreTests();
        NSData *coreData = [[NSString stringWithUTF8String:coreResult] dataUsingEncoding:NSUTF8StringEncoding];
        NSDictionary *coreTests = [NSJSONSerialization JSONObjectWithData:coreData options:0 error:nil];
        NSDictionary *receipt = @{
            @"schema": @1, @"phase": @2, @"nonce": nonce,
            @"event": @"viewDidAppear", @"engine_linked": @NO,
            @"pointer_bits": @(sizeof(void *) * 8), @"core_tests": coreTests,
            @"bundle_id": NSBundle.mainBundle.bundleIdentifier,
            @"system_version": UIDevice.currentDevice.systemVersion,
            @"device_family": UIDevice.currentDevice.userInterfaceIdiom == UIUserInterfaceIdiomPad ? @"iPad" : @"iPhone"
        };
        NSError *error = nil;
        NSData *data = [NSJSONSerialization dataWithJSONObject:receipt options:NSJSONWritingPrettyPrinted error:&error];
        NSURL *directory = [NSFileManager.defaultManager URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask].firstObject;
        if (data == nil || ![data writeToURL:[directory URLByAppendingPathComponent:@"phase02-launch.json"] options:NSDataWritingAtomic error:&error]) {
            NSLog(@"BFG harness receipt failed: %@", error);
        }
    }
#endif
}
@end

@interface HarnessAppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic, strong) UIWindow *window;
@end

@implementation HarnessAppDelegate
- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)options {
    (void)application;
    (void)options;
    self.window = [[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
    self.window.rootViewController = [[HarnessViewController alloc] init];
    [self.window makeKeyAndVisible];
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass(HarnessAppDelegate.class));
    }
}
