using MyAlias=  MyNamespace;
using AnotherAlias = AnotherNamespace;

namespace MyNamespace
{
    class MyClass { }
}

namespace AnotherNamespace
{
    class MyClass { }

    class Program
    {
        static void Main()
        {
            // Using aliases to differentiate between conflucting namespaces
            MyAlias.MyClass myObject1 = new MyAlias.MyClass();
            AnotherAlias.MyClass myObject2 = new AnotherAlias.MyClass();
        }
    }
}