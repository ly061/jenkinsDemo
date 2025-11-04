import org.testng.annotations.*;
import org.testng.Assert;
import java.util.concurrent.TimeUnit;

/**
 * TestNG 测试用例示例
 * 包含三条测试用例
 */
public class TestNGTestCases {
    
    @BeforeClass
    public void setUp() {
        System.out.println("=== 测试类初始化 ===");
        // 在这里可以进行测试前的准备工作
    }
    
    @AfterClass
    public void tearDown() {
        System.out.println("=== 测试类清理 ===");
        // 在这里可以进行测试后的清理工作
    }
    
    @BeforeMethod
    public void beforeMethod() {
        System.out.println("--- 测试方法执行前 ---");
    }
    
    @AfterMethod
    public void afterMethod() {
        System.out.println("--- 测试方法执行后 ---");
    }
    
    /**
     * 测试用例1: 验证字符串相等
     */
    @Test(priority = 1, description = "测试用例1: 验证字符串相等")
    public void testCase1_StringEquals() {
        System.out.println("执行测试用例1: 验证字符串相等");
        String expected = "Hello TestNG";
        String actual = "Hello TestNG";
        Assert.assertEquals(actual, expected, "字符串应该相等");
        System.out.println("测试用例1通过: 字符串相等验证成功");
    }
    
    /**
     * 测试用例2: 验证数字计算
     */
    @Test(priority = 2, description = "测试用例2: 验证数字计算")
    public void testCase2_NumberCalculation() {
        System.out.println("执行测试用例2: 验证数字计算");
        int a = 10;
        int b = 20;
        int sum = a + b;
        Assert.assertEquals(sum, 30, "计算结果应该等于30");
        System.out.println("测试用例2通过: 数字计算验证成功");
    }
    
    /**
     * 测试用例3: 验证数组不为空
     */
    @Test(priority = 3, description = "测试用例3: 验证数组不为空")
    public void testCase3_ArrayNotEmpty() {
        System.out.println("执行测试用例3: 验证数组不为空");
        String[] testArray = {"元素1", "元素2", "元素3"};
        Assert.assertNotNull(testArray, "数组不应该为null");
        Assert.assertTrue(testArray.length > 0, "数组应该包含元素");
        System.out.println("测试用例3通过: 数组验证成功");
    }
    
    /**
     * 可选: 数据驱动测试示例
     */
    @DataProvider(name = "testData")
    public Object[][] provideTestData() {
        return new Object[][] {
            {1, 2, 3},
            {5, 10, 15},
            {100, 200, 300}
        };
    }
    
    @Test(dataProvider = "testData", enabled = false)
    public void dataDrivenTest(int a, int b, int expectedSum) {
        int actualSum = a + b;
        Assert.assertEquals(actualSum, expectedSum, 
            String.format("%d + %d 应该等于 %d", a, b, expectedSum));
    }
}

