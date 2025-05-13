using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Threading.Tasks;
using RobotArmSimulator;
using System;

namespace RobotArmSimulator.Tests
{
    [TestClass]
    public class RobotTests
    {
        private static readonly Random _random = new Random();

        private async Task SimulateTest(Robot robot, int delayMs, double failProbability = 0.2)
        {
            await Task.Delay(delayMs);
            robot.MoveTo(1, 2, 3);
            if (_random.NextDouble() < failProbability)
                Assert.Fail("Randomized simulated failure for test scheduling analysis.");
        }

        [TestMethod]
        [TestCategory("TestCaseId:3")]
        public async Task Test01() => await SimulateTest(new Robot(), 1000, 0.1); // 10% fail

        [TestMethod]
        [TestCategory("TestCaseId:4")]
        public async Task Test02() => await SimulateTest(new Robot(), 2000, 0.5); // 50% fail

        [TestMethod]
        [TestCategory("TestCaseId:5")]
        public async Task Test03() => await SimulateTest(new Robot(), 3000, 0.2); // 20% fail

        [TestMethod]
        [TestCategory("TestCaseId:6")]
        public async Task Test04() => await SimulateTest(new Robot(), 4000, 0.0); // never fail

        [TestMethod]
        [TestCategory("TestCaseId:7")]
        public async Task Test05() => await SimulateTest(new Robot(), 1000, 1.0); // always fail

        [TestMethod]
        [TestCategory("TestCaseId:8")]
        public async Task Test06() => await SimulateTest(new Robot(), 2000, 0.3);

        [TestMethod]
        [TestCategory("TestCaseId:9")]
        public async Task Test07() => await SimulateTest(new Robot(), 3000, 0.6);

        [TestMethod]
        [TestCategory("TestCaseId:10")]
        public async Task Test08() => await SimulateTest(new Robot(), 4000, 0.0);

        [TestMethod]
        [TestCategory("TestCaseId:11")]
        public async Task Test09() => await SimulateTest(new Robot(), 1000, 0.2);

        [TestMethod]
        [TestCategory("TestCaseId:12")]
        public async Task Test10() => await SimulateTest(new Robot(), 2000, 0.4);

        [TestMethod]
        [TestCategory("TestCaseId:13")]
        public async Task Test11() => await SimulateTest(new Robot(), 3000, 0.5);

        [TestMethod]
        [TestCategory("TestCaseId:14")]
        public async Task Test12() => await SimulateTest(new Robot(), 4000, 0.05);

        [TestMethod]
        [TestCategory("TestCaseId:15")]
        public async Task Test13() => await SimulateTest(new Robot(), 5000, 0.3);

        [TestMethod]
        [TestCategory("TestCaseId:16")]
        public async Task Test14() => await SimulateTest(new Robot(), 3000, 0.2);

        [TestMethod]
        [TestCategory("TestCaseId:17")]
        public async Task Test15() => await SimulateTest(new Robot(), 5000, 0.15);

        [TestMethod]
        [TestCategory("TestCaseId:18")]
        public async Task Test16() => await SimulateTest(new Robot(), 2000, 0.25);

        [TestMethod]
        [TestCategory("TestCaseId:19")]
        public async Task Test17() => await SimulateTest(new Robot(), 2000, 0.1);

        [TestMethod]
        [TestCategory("TestCaseId:20")]
        public async Task Test18() => await SimulateTest(new Robot(), 3000, 0.0);

        [TestMethod]
        [TestCategory("TestCaseId:21")]
        public async Task Test19() => await SimulateTest(new Robot(), 1000, 0.05);

        [TestMethod]
        [TestCategory("TestCaseId:22")]
        public async Task Test20() => await SimulateTest(new Robot(), 4000, 0.35);
    }
}
