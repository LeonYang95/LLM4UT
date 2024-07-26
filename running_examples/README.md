# Running Examples of Our Study.


## Prompt Design

### Natural Language Description


    ### Instruction:
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    
    The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
    ```
    public DefaultKeyedValues2D(boolean sortRowKeys);
    public DefaultKeyedValues2D(); 
    ```
    These are the fields defined in the class:
    ```
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    ```
    These are the methods defined in the class :
    ```
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    ```
    This is the method that you are going to test.
    ```
    public void removeColumn(Comparable columnKey) {
        ...
    }
    ```
    The parameter of the method is `columnKey`.
    The parameters come from class `Comparable`.
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    。。。
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


### Code Language Description

Below is an example prompt used for DeepSeek-Coder models.


    ### Instrucion
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    ```
    // The method belongs to the class:
    org.jfree.data.DefaultKeyedValues2D
    
    // Fields
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    
    // Other methods
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    
    // The following code is the method that you are going to test.
    public void removeColumn(Comparable columnKey) {
        ...
    }
    
    // The parameter of the method:
    columnKey
    
    // The parameters come from:
    Comparable
    ```
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    ...
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


## Prompt with In-Context-Learning Techniques.

### Chain-of-Thoughts (CoT)

### Retrieval-Augmented Generation (RAG)


## Illustration Examples of Reasons of Undetected Defects.

### Insufficient Test Coverage

### Missing Specific Inputs

### Improper Assertion


