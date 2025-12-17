using System;
using System.IO.Compression;

namespace MyNamespace
{
    class MyClass {} 

    class Program
    {
        static void Main()
        {
            // Using fully qualified name to avoid naming conflict
            MyNamespace.MyClass myObject = new MyNamespace.MyClass();
        }
    }
}