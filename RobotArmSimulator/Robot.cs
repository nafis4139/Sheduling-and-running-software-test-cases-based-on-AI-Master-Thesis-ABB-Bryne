using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RobotArmSimulator
{
    public class Robot
    {
        public (int X, int Y, int Z) Position { get; private set; } = (0, 0, 0);
        public bool HasObject { get; private set; } = false;

        public void MoveTo(int x, int y, int z)
        {
            if (x < 0 || y < 0 || z < 0)
                throw new ArgumentException("Invalid coordinates");
            Position = (x, y, z);
        }

        public void Pick()
        {
            if (HasObject)
                throw new InvalidOperationException("Already holding object");
            HasObject = true;
        }

        public void Place()
        {
            if (!HasObject)
                throw new InvalidOperationException("Not holding any object");
            HasObject = false;
        }

        public string GetStatus()
        {
            return $"Position: {Position}, Holding: {HasObject}";
        }
    }
}

