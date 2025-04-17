using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Threading.Tasks;
using RobotArmSimulator;

namespace RobotArmSimulator.Tests
{
    [TestClass]
    public class RobotTests
    {
        [TestMethod]
        public async Task ShortTest()
        {
            var robot = new Robot();
            await Task.Delay(1000); // Simulate 1 second
            robot.MoveTo(1, 2, 3);
            Assert.AreEqual((1, 2, 3), robot.Position);
        }

        [TestMethod]
        public async Task MediumTest()
        {
            var robot = new Robot();
            await Task.Delay(5000); // Simulate 5 seconds
            robot.Pick();
            Assert.IsTrue(robot.HasObject);
        }

        [TestMethod]
        public async Task LongTest()
        {
            var robot = new Robot();
            await Task.Delay(30000); // Simulate 1 minute
            robot.MoveTo(5, 5, 5);
            robot.Pick();
            robot.Place();
            Assert.AreEqual((5, 5, 5), robot.Position);
            Assert.IsFalse(robot.HasObject);
        }
    }
}
